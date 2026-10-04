import React, { useState, useEffect } from 'react';
import { voiceManager, VoiceSettings } from '../../services/voiceService';
import { Volume2, Sliders, X, Check, Play, Sparkles, Globe } from 'lucide-react';

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

  useEffect(() => {
    if (!isOpen) return;

    const available = voiceManager.getAvailableVoices();
    setVoices(available);

    const currentSettings = voiceManager.getVoiceSettings();
    setSettings(currentSettings);

    const activeVoice = voiceManager.selectBestVoice(language);
    setActiveVoiceName(currentSettings.voiceName || activeVoice?.name || '');
  }, [isOpen, language]);

  if (!isOpen) return null;

  const handleSelectVoice = (name: string) => {
    setActiveVoiceName(name);
    voiceManager.setVoiceSettings({ voiceName: name });
    setSettings(voiceManager.getVoiceSettings());
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
    voiceManager.testVoice(
      "Hello! I am Professor Elena, your AI teacher. Ready to explore this concept step by step?",
      language
    );
  };

  const handleResetDefaults = () => {
    voiceManager.setVoiceSettings({
      rate: 0.98,
      pitch: 1.05,
      voiceName: null,
    });
    const best = voiceManager.selectBestVoice(language);
    setActiveVoiceName(best?.name || '');
    setSettings(voiceManager.getVoiceSettings());
  };

  // Curate recommended voices
  const recommendedVoices = voices.filter((v) => {
    const n = v.name.toLowerCase();
    return (
      n.includes('natural') ||
      n.includes('aria') ||
      n.includes('jenny') ||
      n.includes('neerja') ||
      n.includes('swara') ||
      n.includes('zira') ||
      n.includes('samantha') ||
      n.includes('victoria') ||
      n.includes('uk english female')
    );
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sliders size={18} />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Prof. Elena — Voice Settings</h3>
              <p className="text-xs text-slate-400">Calibrate speech tone, accent, and cadence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-sm text-slate-300">
          {/* Quick Preview & Test */}
          <div className="bg-gradient-to-r from-blue-900/30 to-indigo-900/30 border border-blue-500/30 rounded-xl p-4 flex items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-300 mb-0.5">
                <Sparkles size={14} /> Active Teacher Voice
              </div>
              <p className="text-xs text-slate-300 font-medium truncate max-w-[260px]">
                {activeVoiceName || 'Default Natural Teacher Voice'}
              </p>
            </div>
            <button
              onClick={handleTestVoice}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all flex-shrink-0"
            >
              <Play size={13} className="fill-white" />
              <span>Test Voice</span>
            </button>
          </div>

          {/* Speed & Pitch Controls */}
          <div className="space-y-4 bg-slate-950/40 p-4 rounded-xl border border-slate-800">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-medium text-slate-300">Speaking Pace (Speed)</span>
                <span className="text-blue-400 font-mono">{settings.rate.toFixed(2)}x</span>
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
                <span>Relaxed (0.75x)</span>
                <span>Normal (1.0x)</span>
                <span>Fast (1.35x)</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-medium text-slate-300">Voice Pitch (Warmth & Tone)</span>
                <span className="text-indigo-400 font-mono">{settings.pitch.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.85"
                max="1.3"
                step="0.05"
                value={settings.pitch}
                onChange={(e) => handlePitchChange(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>Deeper</span>
                <span>Warm Academic (1.05)</span>
                <span>Higher</span>
              </div>
            </div>
          </div>

          {/* Voice Selection List */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Select Voice for Prof. Elena
              </label>
              <button
                type="button"
                onClick={handleResetDefaults}
                className="text-[11px] text-blue-400 hover:text-blue-300 transition-colors"
              >
                Reset to Recommended
              </button>
            </div>

            <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
              {/* Recommended natural voices first */}
              {recommendedVoices.length > 0 && (
                <div className="text-[11px] font-semibold text-slate-500 px-1 pt-1">
                  🌟 RECOMMENDED NATURAL VOICES
                </div>
              )}
              {recommendedVoices.map((v) => (
                <button
                  key={v.name}
                  type="button"
                  onClick={() => handleSelectVoice(v.name)}
                  className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center justify-between transition-all border ${
                    activeVoiceName === v.name
                      ? 'bg-blue-600/20 border-blue-500/60 text-blue-200'
                      : 'bg-slate-800/50 border-slate-700/40 text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex flex-col truncate pr-2">
                    <span className="font-medium truncate">{v.name}</span>
                    <span className="text-[10px] text-slate-400">{v.lang}</span>
                  </div>
                  {activeVoiceName === v.name && <Check size={15} className="text-blue-400 flex-shrink-0" />}
                </button>
              ))}

              {/* All other installed voices */}
              <div className="text-[11px] font-semibold text-slate-500 px-1 pt-2">
                ALL SYSTEM VOICES
              </div>
              {voices
                .filter((v) => !recommendedVoices.some((r) => r.name === v.name))
                .map((v) => (
                  <button
                    key={v.name}
                    type="button"
                    onClick={() => handleSelectVoice(v.name)}
                    className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center justify-between transition-all border ${
                      activeVoiceName === v.name
                        ? 'bg-blue-600/20 border-blue-500/60 text-blue-200'
                        : 'bg-slate-800/30 border-slate-700/30 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex flex-col truncate pr-2">
                      <span className="font-medium truncate">{v.name}</span>
                      <span className="text-[10px] text-slate-500">{v.lang}</span>
                    </div>
                    {activeVoiceName === v.name && <Check size={15} className="text-blue-400 flex-shrink-0" />}
                  </button>
                ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition-all shadow-md"
          >
            Apply & Continue Lesson
          </button>
        </div>
      </div>
    </div>
  );
};
