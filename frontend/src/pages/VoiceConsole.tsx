import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Mic, MicOff, Volume2, Radio, Sliders, Zap, Square, CheckCircle } from 'lucide-react';

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
  const [wakeWordDetected, setWakeWordDetected] = useState<boolean>(true);
  const [lastInteraction, setLastInteraction] = useState<VoiceInteractionResponse | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

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
  }, []);

  const handleVoiceInteract = async () => {
    setIsLoading(true);
    setIsListening(true);
    try {
      const resp = await api.post<VoiceInteractionResponse>('/voice/interact', {
        text_prompt: voicePrompt,
        allow_interruption: true,
      });
      setLastInteraction(resp.data);
      setWakeWordDetected(true);
      setStatusMsg(`✓ Voice interaction complete! Total pipeline latency: ${resp.data.latency_ms}ms.`);
    } catch (err: any) {
      setStatusMsg(`❌ Voice interaction error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
      setIsListening(false);
    }
  };

  const handleInterrupt = async () => {
    try {
      await api.post('/voice/interrupt');
      setStatusMsg('🛑 Speech synthesis interrupted (barge-in active).');
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Mic color="#06b6d4" />
            <span>Voice Assistant Subsystem Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            "Hey JARVIS" Wake Word Detection, Low-Latency STT, Streaming TTS, Interruption Barge-In & Voice Profiles.
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
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Microphone Waveform & Voice Interaction Card */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '90px', height: '90px', borderRadius: '50%', background: isListening ? 'rgba(6, 182, 212, 0.3)' : 'rgba(15, 23, 42, 0.8)', border: isListening ? '2px solid #06b6d4' : '1px solid var(--border-color)', marginBottom: '1.25rem', transition: 'all 0.3s ease' }}>
          <Mic size={38} color={isListening ? '#06b6d4' : '#94a3b8'} />
        </div>

        <div style={{ maxWidth: '600px', margin: '0 auto 1.25rem auto' }}>
          <input
            type="text"
            value={voicePrompt}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setVoicePrompt(e.target.value)}
            placeholder="Speak or type prompt..."
            style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', textAlign: 'center', fontSize: '1rem' }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
          <button onClick={handleVoiceInteract} disabled={isLoading} className="btn-primary" style={{ padding: '0.75rem 2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Radio size={16} />
            <span>Speak / Process Voice Interaction</span>
          </button>
          <button onClick={handleInterrupt} className="btn-primary" style={{ background: '#ef4444', padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Square size={16} />
            <span>Interrupt Barge-In</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Latency Telemetry & Response Player */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="#06b6d4" />
            <span>Latency Optimization & Audio Response</span>
          </h2>

          {lastInteraction ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Recognized STT Transcript</div>
                <div style={{ color: '#38bdf8', fontWeight: 600, fontSize: '0.95rem' }}>"{lastInteraction.transcript}"</div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>JARVIS Spoken Response</div>
                <div style={{ color: '#fff', fontSize: '0.95rem' }}>{lastInteraction.response_text}</div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pipeline Latency</div>
                  <div style={{ color: '#10b981', fontWeight: 700, fontSize: '1.1rem' }}>{lastInteraction.latency_ms} ms</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Barge-In Interrupted</div>
                  <div style={{ color: lastInteraction.interrupted ? '#ef4444' : '#10b981', fontWeight: 700 }}>
                    {lastInteraction.interrupted ? 'YES (Halted)' : 'NO (Clear)'}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem', fontSize: '0.85rem' }}>
              No voice interaction recorded yet. Speak a prompt to view streaming audio response and latency metrics.
            </div>
          )}
        </div>

        {/* Voice Profile Selector Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={18} color="#a78bfa" />
            <span>Voice Profile Customizer</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {profiles.map((prof: VoiceProfile) => (
              <div
                key={prof.profile_id}
                onClick={() => handleProfileSelect(prof.profile_id)}
                style={{
                  background: prof.is_active ? 'rgba(6, 182, 212, 0.15)' : 'rgba(15, 23, 42, 0.6)',
                  border: prof.is_active ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                  padding: '0.85rem 1rem',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
              >
                <div>
                  <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>{prof.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Pitch: {prof.pitch}x | Speed: {prof.speed}x | Voice ID: {prof.voice_id}
                  </div>
                </div>
                {prof.is_active && <span className="badge-success">ACTIVE VOICE</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
