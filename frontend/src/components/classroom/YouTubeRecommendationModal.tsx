import React, { useState, useEffect } from 'react';
import { Youtube, Clock, Sparkles, X, Search, Loader2 } from 'lucide-react';
import { learningVideoService } from '../../services/learningVideoService';
import { YouTubeVideoCard } from '../visual_renderers/YouTubeVideoCard';
import { YouTubeVideoMetadata } from '../../types';

interface YouTubeRecommendationModalProps {
  initialTopic?: string;
  initialDurationMinutes?: number;
  onClose: () => void;
}

export const YouTubeRecommendationModal: React.FC<YouTubeRecommendationModalProps> = ({
  initialTopic = '',
  initialDurationMinutes = 20,
  onClose,
}) => {
  const [topic, setTopic] = useState<string>(initialTopic);
  const [durationMinutes, setDurationMinutes] = useState<number>(initialDurationMinutes);
  const [durationPref, setDurationPref] = useState<string>('around');
  const [learnerLevel, setLearnerLevel] = useState<string>('beginner');
  const [loading, setLoading] = useState<boolean>(false);
  const [videoResult, setVideoResult] = useState<YouTubeVideoMetadata | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setErrorMsg(null);
    setVideoResult(null);

    try {
      const response = await learningVideoService.findLearningVideo(
        topic,
        durationMinutes,
        durationPref,
        learnerLevel
      );

      if (response.found && response.video) {
        setVideoResult(response.video);
      } else {
        setErrorMsg(response.reason || 'No suitable video found for the requested criteria.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to retrieve YouTube video recommendation.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialTopic) {
      handleSearch();
    }
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-hidden relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          title="Close Modal"
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-2 text-red-400 font-semibold text-sm mb-1">
          <Youtube size={20} />
          <span>AI-Powered YouTube Learning Hub</span>
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Duration-Aware Video Recommendation</h3>
        <p className="text-xs text-slate-400 mb-4">
          Searches official YouTube Data API v3 and evaluates candidates to find <strong>EXACTLY ONE</strong> best learning video matching your topic and time limit.
        </p>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-3 mb-5">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="What topic do you want to learn? (e.g. Recursion, React Hooks, Docker)"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full bg-slate-950 text-slate-100 text-xs rounded-xl pl-9 pr-3 py-2.5 border border-slate-700 focus:outline-none focus:border-red-500"
              />
            </div>

            <select
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(Number(e.target.value))}
              className="bg-slate-950 text-slate-200 text-xs rounded-xl px-3 py-2.5 border border-slate-700 focus:outline-none focus:border-red-500 font-medium"
            >
              <option value={10}>~10 min (Speed)</option>
              <option value={20}>~20 min (Concept)</option>
              <option value={30}>~30 min (Tutorial)</option>
              <option value={60}>~60 min (Masterclass)</option>
              <option value={90}>~90 min (Comprehensive)</option>
            </select>

            <select
              value={durationPref}
              onChange={(e) => setDurationPref(e.target.value)}
              className="bg-slate-950 text-slate-200 text-xs rounded-xl px-3 py-2.5 border border-slate-700 focus:outline-none focus:border-red-500 font-medium"
            >
              <option value="around">Around Time</option>
              <option value="under">Under (Max Limit)</option>
              <option value="minimum">At least (60m+)</option>
              <option value="short">Short Overview</option>
              <option value="detailed">In-Depth Detailed</option>
            </select>

            <button
              type="submit"
              disabled={loading || !topic.trim()}
              className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
              <span>{loading ? 'Finding...' : 'Find Best Video'}</span>
            </button>
          </div>
        </form>

        {/* Results Area */}
        <div className="min-h-[160px] flex items-center justify-center">
          {loading ? (
            <div className="text-center py-8">
              <Loader2 size={32} className="animate-spin text-red-500 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-medium">
                Searching YouTube Data API v3 & ranking candidates for duration accuracy...
              </p>
            </div>
          ) : videoResult ? (
            <div className="w-full">
              <YouTubeVideoCard video={videoResult} />
            </div>
          ) : errorMsg ? (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-center text-xs text-slate-400 w-full">
              <p className="text-amber-400 font-medium mb-1">Notice</p>
              <p>{errorMsg}</p>
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500 text-xs">
              <Youtube size={36} className="mx-auto mb-2 opacity-40 text-red-500" />
              <p>Enter any subject topic and target learning duration above to find your verified video.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
