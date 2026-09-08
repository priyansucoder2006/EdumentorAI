import React, { useState, useEffect, useRef } from 'react';
import { videoService, VideoJob } from '../../services/videoService';
import { X, Play, Pause, Video, Sparkles, AlertCircle, Download, CheckCircle2, Volume2, VolumeX, RotateCcw } from 'lucide-react';

interface VideoPlayerModalProps {
  lessonId: string;
  lessonTopic: string;
  onClose: () => void;
}

export const VideoPlayerModal: React.FC<VideoPlayerModalProps> = ({
  lessonId,
  lessonTopic,
  onClose,
}) => {
  const [job, setJob] = useState<VideoJob | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [needsUserPlay, setNeedsUserPlay] = useState<boolean>(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    let intervalId: any = null;

    const startOrCheckJob = async (forceRegenerate: boolean = false) => {
      try {
        setLoading(true);
        setError(null);
        const newJob = await videoService.generateVideo(lessonId);
        setJob(newJob);

        if (newJob.status === 'completed' || newJob.status === 'failed') {
          setLoading(false);
          return;
        }

        intervalId = setInterval(async () => {
          try {
            const current = await videoService.getJobStatus(newJob.id);
            setJob(current);
            if (current.status === 'completed' || current.status === 'failed') {
              clearInterval(intervalId);
            }
          } catch (err: any) {
            console.error('Video status poll error:', err);
          }
        }, 1200);
      } catch (err: any) {
        setError(err.message || 'Failed to initialize video generation.');
      } finally {
        setLoading(false);
      }
    };

    startOrCheckJob();

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [lessonId]);

  const handleVideoLoaded = () => {
    if (videoRef.current) {
      videoRef.current.volume = 1.0;
      videoRef.current.muted = false;
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            setIsPlaying(true);
            setNeedsUserPlay(false);
          })
          .catch(() => {
            // Browser autoplay policy blocked un-muted sound
            setNeedsUserPlay(true);
            setIsPlaying(false);
          });
      }
    }
  };

  const handleManualPlayWithSound = () => {
    if (videoRef.current) {
      videoRef.current.volume = 1.0;
      videoRef.current.muted = false;
      setIsMuted(false);
      videoRef.current.play().then(() => {
        setIsPlaying(true);
        setNeedsUserPlay(false);
      });
    }
  };

  const handleTogglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
      setNeedsUserPlay(false);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleToggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !videoRef.current.muted;
    setIsMuted(videoRef.current.muted);
  };

  const handleRestart = () => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = 0;
    videoRef.current.play();
    setIsPlaying(true);
    setNeedsUserPlay(false);
  };

  const isCompleted = job?.status === 'completed' && job.video_url;
  const isFailed = job?.status === 'failed';
  const progress = job?.progress || 0;
  const displayProgress = isCompleted ? 100 : Math.max(5, progress);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400">
              <Video size={20} />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">AI Master Video Lesson</h3>
              <p className="text-xs text-slate-400">{lessonTopic}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 flex flex-col items-center justify-center min-h-[380px]">
          {error || isFailed ? (
            <div className="text-center max-w-md">
              <AlertCircle size={48} className="text-rose-400 mx-auto mb-3" />
              <h4 className="text-lg font-medium text-white mb-1">Video Generation Failed</h4>
              <p className="text-sm text-slate-400 mb-4">{error || job?.error_message || 'An error occurred during video rendering.'}</p>
              <button onClick={onClose} className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm">
                Close
              </button>
            </div>
          ) : isCompleted ? (
            <div className="w-full flex flex-col items-center">
              {/* HTML5 Native Video Player with Sound Overlay */}
              <div className="w-full aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 shadow-inner relative group">
                <video
                  ref={videoRef}
                  controls
                  playsInline
                  onLoadedMetadata={handleVideoLoaded}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  className="w-full h-full object-contain"
                  src={job.video_url.startsWith('http') ? job.video_url : `http://localhost:8000${job.video_url}`}
                >
                  Your browser does not support the video tag.
                </video>

                {/* Autoplay blocked sound banner */}
                {needsUserPlay && (
                  <div className="absolute inset-0 bg-black/60 backdrop-blur-xs flex flex-col items-center justify-center gap-3 transition-opacity">
                    <button
                      onClick={handleManualPlayWithSound}
                      className="flex items-center gap-3 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-xl transform hover:scale-105 transition-all text-base"
                    >
                      <Volume2 size={24} className="animate-pulse" />
                      <span>Click to Play with Voice Audio</span>
                    </button>
                    <p className="text-xs text-slate-300">Browser requires one click to enable teacher voice narration</p>
                  </div>
                )}
              </div>

              {/* Quick Sound & Playback Bar */}
              <div className="flex items-center justify-between w-full mt-3 px-2 py-2 bg-slate-800/60 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleTogglePlay}
                    className="p-1.5 rounded-md hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? <Pause size={17} /> : <Play size={17} />}
                  </button>
                  <button
                    onClick={handleRestart}
                    className="p-1.5 rounded-md hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    title="Restart from beginning"
                  >
                    <RotateCcw size={16} />
                  </button>
                  <button
                    onClick={handleToggleMute}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-700/70 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
                    title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
                  >
                    {isMuted ? <VolumeX size={15} className="text-rose-400" /> : <Volume2 size={15} className="text-cyan-400" />}
                    <span>{isMuted ? 'Muted' : 'Sound: 100%'}</span>
                  </button>
                </div>

                <div className="flex items-center gap-2 text-xs text-cyan-300 font-medium">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span>Synchronized AI Voice Audio: Active</span>
                </div>
              </div>

              {/* Footer Actions */}
              <div className="flex items-center justify-between w-full mt-4">
                <div className="flex items-center gap-2 text-emerald-400 text-sm">
                  <CheckCircle2 size={16} />
                  <span>Production H.264 MP4 with animated avatar & synchronized voice narration</span>
                </div>
                <a
                  href={job.video_url.startsWith('http') ? job.video_url : `http://localhost:8000${job.video_url}`}
                  download
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  <Download size={15} />
                  <span>Download MP4</span>
                </a>
              </div>
            </div>
          ) : (
            /* Progress & Rendering State */
            <div className="text-center max-w-lg w-full py-8">
              <div className="relative w-20 h-20 mx-auto mb-6">
                <div className="absolute inset-0 rounded-full border-4 border-blue-500/20 animate-ping" />
                <div className="w-20 h-20 rounded-full bg-blue-600/10 border-2 border-blue-500 flex items-center justify-center text-blue-400">
                  <Sparkles size={32} className="animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              </div>

              <h4 className="text-xl font-semibold text-white mb-2">
                Synthesizing AI Teaching Video...
              </h4>
              <p className="text-sm text-slate-400 mb-6">
                Compositing pedagogical scenes, LaTeX visual boards, animated avatar, and synchronized voice narration into an MP4 file.
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden mb-3 border border-slate-700">
                <div
                  className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full transition-all duration-500 ease-out"
                  style={{ width: `${displayProgress}%` }}
                />
              </div>

              <div className="flex justify-between text-xs text-slate-400">
                <span>
                  {displayProgress < 20
                    ? 'Planning Storyboard Scenes...'
                    : displayProgress < 60
                    ? 'Synthesizing Spoken Narration...'
                    : displayProgress < 90
                    ? 'Rendering Visual Boards & Avatar PIP...'
                    : 'Muxing MP4 Video & Audio Streams...'}
                </span>
                <span className="font-mono text-cyan-400 font-bold">{displayProgress}%</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
