import React, { useState, useEffect, useMemo } from 'react';
import { voiceManager, VoiceSettings } from '../../services/voiceService';
import {
  Volume2,
  Sliders,
  X,
  Check,
  Play,
  Square,
  Sparkles,
  Globe,
  Search,
  RotateCcw,
  AlertCircle,
} from 'lucide-react';

interface VoiceSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  language?: string;
}

export const VoiceSettingsModal: React.FC<VoiceSettingsModalProps> = ({
  isOpen,
  onClose,
  language = 'en',
}) => {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [settings, setSettings] = useState<VoiceSettings>(voiceManager.getVoiceSettings());
  const [activeVoiceName, setActiveVoiceName] = useState<string>('');
  const [isPlayingTest, setIsPlayingTest] = useState<boolean>(false);
  const [previewingVoiceName, setPreviewingVoiceName] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'language' | 'all'>('language');

  const langKey = useMemo(() => (language || 'en').toLowerCase().split('-')[0], [language]);

  const languageDisplayName = useMemo(() => {
    switch (langKey) {
      case 'bn':
        return 'Bengali (বাংলা)';
      case 'hi':
        return 'Hindi (हिन्दी)';
      case 'es':
        return 'Spanish (Español)';
      case 'fr':
        return 'French (Français)';
      case 'de':
        return 'German (Deutsch)';
      default:
        return 'English';
    }
  }, [langKey]);

  // Sync available voices and current voice settings
  useEffect(() => {
    if (!isOpen) return;

    const refreshVoiceState = () => {
      const available = voiceManager.getAvailableVoices();
      setVoices([...available]);

      const currentSettings = voiceManager.getVoiceSettings();
      setSettings(currentSettings);

      const preferred = voiceManager.getPreferredVoiceForLanguage(language);
      const activeVoice = voiceManager.selectBestVoice(language);
      setActiveVoiceName(preferred || activeVoice?.name || '');
    };

    refreshVoiceState();

    // Subscribe to voice changes (handles delayed browser speech synthesis initialization)
    const unsubscribe = voiceManager.subscribeVoicesChanged(refreshVoiceState);

    const handleBrowserVoicesChanged = () => {
      refreshVoiceState();
    };

    if (typeof window !== 'undefined' && window.speechSynthesis) {
      try {
        window.speechSynthesis.addEventListener('voiceschanged', handleBrowserVoicesChanged);
      } catch {}
    }

    return () => {
      unsubscribe();
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        try {
          window.speechSynthesis.removeEventListener('voiceschanged', handleBrowserVoicesChanged);
        } catch {}
      }
    };
  }, [isOpen, language]);

  // Sync speaking state
  useEffect(() => {
    if (!isOpen) return;

    voiceManager.setSpeakingListener((speaking) => {
      if (!speaking) {
        setIsPlayingTest(false);
        setPreviewingVoiceName(null);
      }
    });

    return () => {
      // Clean up speaking when closing modal
      if (isPlayingTest || previewingVoiceName) {
        voiceManager.stopSpeaking();
      }
    };
  }, [isOpen, isPlayingTest, previewingVoiceName]);

  // Escape key handler
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        voiceManager.stopSpeaking();
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSelectVoice = (voice: SpeechSynthesisVoice) => {
    setActiveVoiceName(voice.name);
    voiceManager.setPreferredVoiceForLanguage(language, voice.name);
    setSettings(voiceManager.getVoiceSettings());

    // Audition selected voice immediately
    setPreviewingVoiceName(voice.name);
    voiceManager.previewVoice(voice, undefined, () => {
      setPreviewingVoiceName(null);
    });
  };

  const handlePreviewVoice = (voice: SpeechSynthesisVoice, e: React.MouseEvent) => {
    e.stopPropagation();
    if (previewingVoiceName === voice.name) {
      voiceManager.stopSpeaking();
      setPreviewingVoiceName(null);
      setIsPlayingTest(false);
      return;
    }

    setPreviewingVoiceName(voice.name);
    setIsPlayingTest(false);
    voiceManager.previewVoice(voice, undefined, () => {
      setPreviewingVoiceName(null);
    });
  };

  const handleRateChange = (rate: number) => {
    setSettings((prev) => ({ ...prev, rate }));
    voiceManager.setVoiceSettings({ rate });
  };

  const handlePitchChange = (pitch: number) => {
    setSettings((prev) => ({ ...prev, pitch }));
    voiceManager.setVoiceSettings({ pitch });
  };

  const handleTestVoice = () => {
    if (isPlayingTest) {
      voiceManager.stopSpeaking();
      setIsPlayingTest(false);
      return;
    }

    setPreviewingVoiceName(null);
    setIsPlayingTest(true);

    voiceManager.testVoice(undefined, language, () => {
      setIsPlayingTest(false);
    });
  };

  const handleResetDefaults = () => {
    voiceManager.clearPreferredVoiceForLanguage(language);
    voiceManager.setVoiceSettings({
      rate: 0.98,
      pitch: 1.05,
      voiceName: null,
    });
    setSettings(voiceManager.getVoiceSettings());

    const best = voiceManager.selectBestVoice(language);
    setActiveVoiceName(best?.name || '');

    if (best) {
      setPreviewingVoiceName(best.name);
      voiceManager.previewVoice(best, undefined, () => {
        setPreviewingVoiceName(null);
      });
    }
  };

  const handleCloseModal = () => {
    voiceManager.stopSpeaking();
    onClose();
  };

  // Check if voice matches language
  const isVoiceForCurrentLang = (v: SpeechSynthesisVoice): boolean => {
    const l = v.lang.toLowerCase();
    const n = v.name.toLowerCase();
    if (langKey === 'bn') {
      return l.startsWith('bn') || n.includes('bengali') || n.includes('bangla');
    }
    if (langKey === 'hi') {
      return l.startsWith('hi') || n.includes('hindi');
    }
    if (langKey === 'en') {
      return l.startsWith('en');
    }
    return l.startsWith(langKey);
  };

  // Identify recommended natural/female voices
  const isRecommendedVoice = (v: SpeechSynthesisVoice): boolean => {
    const n = v.name.toLowerCase();
    const l = v.lang.toLowerCase();

    if (langKey === 'bn') {
      return (
        l.startsWith('bn') ||
        n.includes('bengali') ||
        n.includes('bangla') ||
        n.includes('tanishaa') ||
        n.includes('bashkar')
      );
    }

    if (langKey === 'hi') {
      return l.startsWith('hi') || n.includes('hindi') || n.includes('swara');
    }

    return (
      l.startsWith('en') &&
      (n.includes('aria') ||
        n.includes('jenny') ||
        n.includes('natural') ||
        n.includes('uk english female') ||
        n.includes('samantha') ||
        n.includes('zira') ||
        n.includes('victoria'))
    );
  };

  // Filter voices based on active tab and search query
  const displayedVoices = voices.filter((v) => {
    if (activeTab === 'language' && !isVoiceForCurrentLang(v)) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      return v.name.toLowerCase().includes(q) || v.lang.toLowerCase().includes(q);
    }
    return true;
  });

  const languageVoicesCount = voices.filter(isVoiceForCurrentLang).length;

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in"
      onClick={handleCloseModal}
    >
      <div
        className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col max-h-[88vh] my-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/25">
              <Sliders size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-white">Prof. Elena — Voice Calibration</h3>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  {languageDisplayName}
                </span>
              </div>
              <p className="text-xs text-slate-400">Fine-tune AI Master Teacher pronunciation, cadence, and timbre</p>
            </div>
          </div>
          <button
            onClick={handleCloseModal}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Close"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1 text-sm text-slate-300">
          {/* Active Voice Status Card */}
          <div className="bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/60 border border-blue-500/30 rounded-xl p-4 flex items-center justify-between gap-3 shadow-inner">
            <div className="flex items-center gap-3 min-w-0">
              <div className={`p-2.5 rounded-xl ${isPlayingTest ? 'bg-amber-500/20 text-amber-400 animate-pulse' : 'bg-blue-500/20 text-blue-400'}`}>
                <Volume2 size={20} />
              </div>
              <div className="truncate">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-300 mb-0.5">
                  <Sparkles size={13} /> Active Voice for {languageDisplayName}
                </div>
                <p className="text-sm text-white font-medium truncate">
                  {activeVoiceName || 'System Default Academic Voice'}
                </p>
              </div>
            </div>

            <button
              onClick={handleTestVoice}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold shadow-md transition-all flex-shrink-0 ${
                isPlayingTest
                  ? 'bg-rose-600 hover:bg-rose-500 text-white animate-pulse'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20'
              }`}
            >
              {isPlayingTest ? (
                <>
                  <Square size={13} className="fill-white" />
                  <span>Stop Voice</span>
                </>
              ) : (
                <>
                  <Play size={13} className="fill-white" />
                  <span>Test Voice</span>
                </>
              )}
            </button>
          </div>

          {/* Speed & Pitch Controls */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-medium text-slate-300">Speaking Pace</span>
                <span className="text-blue-400 font-mono font-semibold">{settings.rate.toFixed(2)}x</span>
              </div>
              <input
                type="range"
                min="0.75"
                max="1.35"
                step="0.05"
                value={settings.rate}
                onChange={(e) => handleRateChange(parseFloat(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>0.75x (Relaxed)</span>
                <span>0.98x (Master Teacher)</span>
                <span>1.35x (Fast)</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-medium text-slate-300">Tone Pitch</span>
                <span className="text-indigo-400 font-mono font-semibold">{settings.pitch.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.85"
                max="1.30"
                step="0.05"
                value={settings.pitch}
                onChange={(e) => handlePitchChange(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>Deeper</span>
                <span>1.05 (Academic Warmth)</span>
                <span>Brighter</span>
              </div>
            </div>
          </div>

          {/* Voice Selection Section */}
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Select Voice for Prof. Elena
                </label>
                <p className="text-[11px] text-slate-400">
                  Click any card to select & audition the voice
                </p>
              </div>

              <button
                type="button"
                onClick={handleResetDefaults}
                className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors self-start sm:self-auto py-1 px-2 rounded-md hover:bg-blue-950/40"
              >
                <RotateCcw size={12} />
                <span>Reset to Recommended</span>
              </button>
            </div>

            {/* Filter Tabs & Search Bar */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <div className="flex bg-slate-950/60 p-1 rounded-lg border border-slate-800 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveTab('language')}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                    activeTab === 'language'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {languageDisplayName} ({languageVoicesCount})
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('all')}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                    activeTab === 'all'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  All System Voices ({voices.length})
                </button>
              </div>

              {/* Search input */}
              <div className="relative flex-1">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter voices (e.g. Natural, US, UK, Aria)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  >
                    <X size={12} />
                  </button>
                )}
              </div>
            </div>

            {/* Voices List */}
            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {displayedVoices.length === 0 ? (
                <div className="p-6 text-center bg-slate-950/40 rounded-xl border border-slate-800/80">
                  <AlertCircle size={22} className="mx-auto text-amber-400/80 mb-2" />
                  <p className="text-xs text-slate-300 font-medium">No matching voices found</p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    {searchQuery
                      ? 'Try clearing the search filter.'
                      : `Your system might not have local ${languageDisplayName} voices installed. Switch to "All System Voices" tab to choose another voice.`}
                  </p>
                </div>
              ) : (
                displayedVoices.map((v, idx) => {
                  const isSelected = activeVoiceName === v.name;
                  const isPreviewing = previewingVoiceName === v.name;
                  const isRec = isRecommendedVoice(v);

                  return (
                    <div
                      key={`${v.name}-${v.lang}-${idx}`}
                      onClick={() => handleSelectVoice(v)}
                      className={`group w-full p-3 rounded-xl text-xs flex items-center justify-between transition-all border cursor-pointer ${
                        isSelected
                          ? 'bg-blue-600/15 border-blue-500/70 text-blue-100 shadow-sm shadow-blue-500/10'
                          : 'bg-slate-950/40 border-slate-800/80 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0 pr-2">
                        {/* Play preview button */}
                        <button
                          type="button"
                          onClick={(e) => handlePreviewVoice(v, e)}
                          title={isPreviewing ? 'Stop Preview' : 'Preview this voice'}
                          className={`p-2 rounded-lg flex-shrink-0 transition-all ${
                            isPreviewing
                              ? 'bg-amber-500 text-slate-950 shadow-md animate-pulse'
                              : 'bg-slate-800/90 text-blue-400 group-hover:bg-blue-600 group-hover:text-white'
                          }`}
                        >
                          {isPreviewing ? <Square size={12} className="fill-current" /> : <Play size={12} className="fill-current ml-0.5" />}
                        </button>

                        <div className="truncate">
                          <div className="flex items-center gap-2 truncate">
                            <span className="font-semibold text-white truncate">{v.name}</span>
                            {isRec && (
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex-shrink-0 flex items-center gap-1">
                                <Sparkles size={10} /> Elena Recommended
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400">
                            <span className="font-mono bg-slate-800/80 px-1.5 py-0.2 rounded text-[10px]">
                              {v.lang}
                            </span>
                            {v.name.includes('Natural') && (
                              <span className="text-emerald-400 text-[10px] font-medium">
                                Natural Neural Audio
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {isSelected && (
                          <div className="flex items-center gap-1 text-[11px] font-semibold text-blue-400 bg-blue-500/10 px-2 py-1 rounded-md border border-blue-500/20">
                            <Check size={14} className="text-blue-400" />
                            <span>Active</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/70 flex items-center justify-between">
          <div className="text-[11px] text-slate-400 hidden sm:block">
            Voice calibration persists automatically across lessons
          </div>
          <button
            onClick={handleCloseModal}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold transition-all shadow-md shadow-blue-500/25 ml-auto"
          >
            Apply & Continue Lesson
          </button>
        </div>
      </div>
    </div>
  );
};

