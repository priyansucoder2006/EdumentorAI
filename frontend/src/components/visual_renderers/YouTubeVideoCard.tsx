import React from 'react';
import { Youtube, ExternalLink, Clock, Sparkles, Video } from 'lucide-react';
import { YouTubeVideoMetadata } from '../../types';

interface YouTubeVideoCardProps {
  video?: YouTubeVideoMetadata;
  title?: string;
  channel?: string;
  duration?: string;
  thumbnail?: string;
  url?: string;
  reason?: string;
}

export const YouTubeVideoCard: React.FC<YouTubeVideoCardProps> = ({
  video,
  title = video?.title || 'Recommended Educational Masterclass',
  channel = video?.channel || 'Verified Educator',
  duration = video?.duration || '20:00',
  thumbnail = video?.thumbnail || '',
  url = video?.url || 'https://www.youtube.com',
  reason = video?.reason || 'Recommended educational resource matching your topic and target duration.',
}) => {
  return (
    <div className="youtube-video-recommendation-card bg-slate-900 border border-slate-700/80 rounded-xl overflow-hidden shadow-xl transition-all hover:border-blue-500/50">
      <div className="p-4 bg-slate-800/60 border-b border-slate-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-400 border border-red-500/30">
            <Youtube size={14} /> YouTube Learning Resource
          </span>
          <span className="text-xs text-slate-400">Duration-Aware Recommendation</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-cyan-400 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-700">
          <Clock size={12} />
          <span>{duration}</span>
        </div>
      </div>

      <div className="p-4 sm:p-5 flex flex-col md:flex-row gap-4 items-start">
        {/* Video Thumbnail with duration overlay */}
        <div className="relative w-full md:w-56 flex-shrink-0 aspect-video rounded-lg overflow-hidden border border-slate-700/60 group">
          {thumbnail ? (
            <img
              src={thumbnail}
              alt={title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-slate-800 flex items-center justify-center text-slate-500">
              <Video size={36} />
            </div>
          )}
          <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors flex items-center justify-center">
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-12 h-12 rounded-full bg-red-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform"
              title="Watch on YouTube"
            >
              <Youtube size={24} />
            </a>
          </div>
          <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 text-white text-[11px] font-mono font-medium">
            {duration}
          </div>
        </div>

        {/* Video Details & Pedagogical Reason */}
        <div className="flex-1 flex flex-col justify-between h-full">
          <div>
            <h4 className="text-base font-semibold text-slate-100 leading-snug line-clamp-2 hover:text-blue-400 transition-colors">
              <a href={url} target="_blank" rel="noopener noreferrer">
                {title}
              </a>
            </h4>
            <p className="text-xs text-slate-400 mt-1 font-medium flex items-center gap-1.5">
              <span>Channel:</span>
              <strong className="text-slate-300">{channel}</strong>
            </p>

            {/* Why this video */}
            <div className="mt-3 p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/50 text-xs text-slate-300">
              <div className="flex items-center gap-1.5 text-blue-400 font-medium mb-1">
                <Sparkles size={13} />
                <span>Why this video:</span>
              </div>
              <p className="text-slate-300/90 leading-relaxed">{reason}</p>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
            <span className="text-[11px] text-slate-500">Official YouTube Data API v3</span>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-md transition-all"
            >
              <Youtube size={15} />
              <span>Watch on YouTube</span>
              <ExternalLink size={12} />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
