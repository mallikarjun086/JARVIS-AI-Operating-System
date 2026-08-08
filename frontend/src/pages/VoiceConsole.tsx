import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { Mic, MicOff, Volume2, Radio, Sliders, Zap, Square, CheckCircle, VolumeX } from 'lucide-react';

interface VoiceProfile {
  profile_id: string;
  name: string;
  pitch: number;
  speed: number;
  voice_id: string;
  is_active: boolean;
}

interface VoiceInteractionResponse {
  interaction_id: string;
  transcript: string;
  response_text: string;
  audio_base64: string;
  interrupted: boolean;
  latency_ms: number;
}

export const VoiceConsolePage: React.FC = () => {
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string>('');
  const [voicePrompt, setVoicePrompt] = useState<string>('Hey JARVIS, run diagnostic check on operating system services');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [wakeWordDetected, setWakeWordDetected] = useState<boolean>(true);
  const [lastInteraction, setLastInteraction] = useState<VoiceInteractionResponse | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

  const fetchProfiles = async () => {
    try {
      const resp = await api.get<VoiceProfile[]>('/voice/profiles');
      setProfiles(resp.data);
      const active = resp.data.find(p => p.is_active);
      if (active) setActiveProfileId(active.profile_id);
    } catch (err) {
      console.error('Error fetching voice profiles', err);
    }
  };

  useEffect(() => {
    fetchProfiles();

    // Initialize Web Speech Recognition if available in browser
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recog = new SpeechRecognition();
      recog.continuous = false;
      recog.interimResults = true;
      recog.lang = 'en-US';

      recog.onresult = (event: any) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setVoicePrompt(transcriptText);
        setWakeWordDetected(transcriptText.toLowerCase().includes('jarvis') || transcriptText.toLowerCase().includes('hey'));
      };

      recog.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recog;
    }
  }, []);

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // stop any ongoing speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 0.95;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleStartListening = () => {
    if (recognitionRef.current) {
      try {
        setIsListening(true);
        setStatusMsg('🎙️ Listening... Speak your prompt into the microphone.');
        recognitionRef.current.start();
      } catch (err) {
        console.error(err);
      }
    } else {
      setStatusMsg('💡 Browser SpeechRecognition unavailable. Type your prompt below.');
    }
  };

  const handleVoiceInteract = async () => {
    if (!voicePrompt.trim()) return;
    setIsLoading(true);
    setStatusMsg('⚡ Processing voice interaction pipeline (STT ➔ LLM Router ➔ TTS)...');
    try {
      const resp = await api.post<VoiceInteractionResponse>('/voice/interact', {
        text_prompt: voicePrompt,
        allow_interruption: true,
      });
      setLastInteraction(resp.data);
      setWakeWordDetected(true);
      setStatusMsg(`✓ Voice interaction complete! Pipeline latency: ${resp.data.latency_ms}ms.`);
      
      // Speak the response using browser TTS
      if (resp.data.response_text) {
        speakText(resp.data.response_text);
      }
    } catch (err: any) {
      setStatusMsg(`❌ Voice interaction error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
      setIsListening(false);
    }
  };

  const handleInterrupt = async () => {
    try {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setIsSpeaking(false);
      await api.post('/voice/interrupt');
      setStatusMsg('🛑 Speech synthesis interrupted (Barge-In active).');
      if (lastInteraction) {
        setLastInteraction({ ...lastInteraction, interrupted: true, audio_base64: '' });
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleProfileSelect = async (profileId: string) => {
    try {
      await api.post(`/voice/profiles/${profileId}/activate`);
      setActiveProfileId(profileId);
      setStatusMsg(`✓ Active voice profile updated.`);
      await fetchProfiles();
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span className="badge-purple">VOICE INTELLIGENCE v1.0</span>
            <span className="beacon-dot"></span>
            <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>STT/TTS STREAMING READY</span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Mic color="#06b6d4" size={26} />
            <span>Voice Assistant Subsystem Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            "Hey JARVIS" Wake Word Detection, Low-Latency STT, Real-Time Audio TTS, Interruption Barge-In & Custom Voice Profiles.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {wakeWordDetected ? (
            <span className="badge-success" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.85rem' }}>
              <Radio size={14} color="#10b981" />
              <span>WAKE WORD DETECTED: "Hey JARVIS"</span>
            </span>
          ) : (
            <span style={{ background: 'rgba(148, 163, 184, 0.2)', color: '#94a3b8', padding: '0.5rem 0.85rem', borderRadius: '20px', fontSize: '0.8rem' }}>
              Listening for "Hey JARVIS"...
            </span>
          )}
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.35)', color: '#7dd3fc', padding: '0.85rem 1.15rem', borderRadius: '10px', marginBottom: '1.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
          {statusMsg}
        </div>
      )}

      {/* Microphone Waveform & Voice Interaction Card */}
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '100px', height: '100px', borderRadius: '50%', background: isListening ? 'rgba(6, 182, 212, 0.35)' : isSpeaking ? 'rgba(139, 92, 246, 0.35)' : 'rgba(10, 14, 26, 0.8)', border: isListening ? '2px solid #06b6d4' : isSpeaking ? '2px solid #8b5cf6' : '1px solid var(--border-color)', marginBottom: '1.25rem', transition: 'all 0.3s ease', cursor: 'pointer' }} onClick={handleStartListening}>
          <Mic size={42} color={isListening ? '#06b6d4' : isSpeaking ? '#c084fc' : '#94a3b8'} />
        </div>

        <div style={{ fontSize: '0.85rem', color: isListening ? '#38bdf8' : isSpeaking ? '#c084fc' : 'var(--text-muted)', marginBottom: '1rem', fontWeight: 600 }}>
          {isListening ? '🎙️ Listening to microphone... Speak now!' : isSpeaking ? '🔊 JARVIS is speaking response...' : 'Click Microphone or type prompt below'}
        </div>

        <div style={{ maxWidth: '650px', margin: '0 auto 1.25rem auto' }}>
          <input
            type="text"
            value={voicePrompt}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setVoicePrompt(e.target.value)}
            placeholder="Speak or type voice prompt..."
            style={{ width: '100%', padding: '0.85rem 1.15rem', borderRadius: '10px', background: 'rgba(10, 14, 26, 0.8)', border: '1px solid var(--border-color)', color: '#fff', textAlign: 'center', fontSize: '1.05rem', fontWeight: 500 }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
          <button onClick={handleStartListening} className="btn-secondary" style={{ padding: '0.75rem 1.5rem' }}>
            <Mic size={16} />
            <span>Listen Mic</span>
          </button>
          <button onClick={handleVoiceInteract} disabled={isLoading} className="btn-primary" style={{ padding: '0.75rem 2rem' }}>
            <Radio size={16} />
            <span>{isLoading ? 'Processing...' : 'Process Voice Interaction'}</span>
          </button>
          <button onClick={handleInterrupt} className="btn-primary" style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)', padding: '0.75rem 1.5rem' }}>
            <Square size={16} />
            <span>Halt / Barge-In</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Latency Telemetry & Response Player */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="#06b6d4" />
            <span>Latency Optimization & Spoken Response</span>
          </h2>

          {lastInteraction ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ background: 'rgba(10, 14, 26, 0.7)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.3rem', fontWeight: 600 }}>Recognized STT Transcript</div>
                <div style={{ color: '#38bdf8', fontWeight: 600, fontSize: '0.95rem' }}>"{lastInteraction.transcript}"</div>
              </div>

              <div style={{ background: 'rgba(10, 14, 26, 0.7)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>JARVIS Spoken Response</span>
                  <button onClick={() => speakText(lastInteraction.response_text)} className="btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}>
                    <Volume2 size={13} /> Replay
                  </button>
                </div>
                <div style={{ color: '#fff', fontSize: '0.95rem', lineHeight: '1.4' }}>{lastInteraction.response_text}</div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(10, 14, 26, 0.7)', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pipeline Latency</div>
                  <div style={{ color: '#10b981', fontWeight: 700, fontSize: '1.1rem' }}>{lastInteraction.latency_ms} ms</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Barge-In Status</div>
                  <div style={{ color: lastInteraction.interrupted ? '#ef4444' : '#10b981', fontWeight: 700 }}>
                    {lastInteraction.interrupted ? 'HALTED (Barge-In)' : 'CLEAR'}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0', fontSize: '0.85rem' }}>
              No voice interaction recorded yet. Speak or process a prompt to view audio response and pipeline latency metrics.
            </div>
          )}
        </div>

        {/* Voice Profile Selector Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={18} color="#a78bfa" />
            <span>Voice Profile Customizer</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {profiles.map((prof: VoiceProfile) => (
              <div
                key={prof.profile_id}
                onClick={() => handleProfileSelect(prof.profile_id)}
                style={{
                  background: prof.is_active ? 'rgba(6, 182, 212, 0.15)' : 'rgba(10, 14, 26, 0.7)',
                  border: prof.is_active ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                  padding: '0.9rem 1.15rem',
                  borderRadius: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
              >
                <div>
                  <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 700 }}>{prof.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    Pitch: {prof.pitch}x | Speed: {prof.speed}x | Voice ID: {prof.voice_id}
                  </div>
                </div>
                {prof.is_active ? (
                  <span className="badge-success">ACTIVE VOICE</span>
                ) : (
                  <span className="badge-info" style={{ opacity: 0.7 }}>ACTIVATE</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

