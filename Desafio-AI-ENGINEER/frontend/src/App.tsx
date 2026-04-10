import { useEffect, useMemo, useState, useRef } from 'react';
import './SentinelPulse.css';
import axios from 'axios';
import { History, Loader2, Upload, Camera, FolderOpen, X, Trash2 } from 'lucide-react';

interface HistoricoItem {
  id: number;
  emocao: string;
  certeza: string;
  url_imagem: string;
  data_hora: string;
  todas_probabilidades: string;
}

interface PredictResponse {
  emocao_principal: string;
  certeza_principal: string;
  todas_probabilidades: Record<string, string>;
  status: string;
  rosto_detectado: boolean;
}

interface HistoryResponse {
  total_registros: number;
  historico: HistoricoItem[];
}

const API = 'http://localhost:5000';

export default function SentinelPulse() {
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [predicaoAtual, setPredicaoAtual] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => { void getHistorico(); }, []);
  useEffect(() => {
    if (!selectedFile) { setPreviewUrl(null); return; }
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const getHistorico = async () => {
    try {
      const result = await axios.get<HistoryResponse>(`${API}/history`);
      setHistorico(result.data.historico ?? []);
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
    }
  };

  const deleteHistorico = async () => {
    try {
      await axios.delete(`${API}/history`);
      setHistorico([]);
      setPredicaoAtual(null);
    } catch (error) {
      console.error('Erro ao deletar histórico:', error);
    }
  };

  const postImage = async () => {
    if (!selectedFile) { setErro('Selecione uma imagem antes de analisar.'); return; }
    setErro(null);
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await axios.post<PredictResponse>(`${API}/predict`, formData);
      setPredicaoAtual(response.data);
      await getHistorico();
      setSelectedFile(null);
    } catch (error: unknown) {
      const isAxios = axios.isAxiosError<{ erro?: string }>(error);
      const message =
        isAxios && error.response?.data?.erro
          ? error.response.data.erro
          : 'Erro ao processar a imagem.';

      if (message === 'Nenhum rosto humano detectado na imagem.') {
        setPredicaoAtual({
          emocao_principal: 'Nenhum rosto humano detectado na imagem.',
          certeza_principal: '100%',
          todas_probabilidades: {},
          status: 'Erro',
          rosto_detectado: false,
        });
        await getHistorico();
        setSelectedFile(null);
        setErro(null);
      } else {
        setErro(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const openCamera = async () => {
    setIsCameraOpen(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Erro ao acessar a câmera:', err);
      setErro('Não foi possível acessar a câmera do dispositivo.');
      setIsCameraOpen(false);
    }
  };

  const closeCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraOpen(false);
  };

  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob) {
            // Em vez de File (que às vezes pode não rolar no mobile Safari/antigos),
            // usar um workaround criando uma propriedade lastModified simulada.
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg', lastModified: Date.now() });
            setSelectedFile(file);
          }
          closeCamera();
        }, 'image/jpeg', 0.9);
      }
    }
  };

  const secondaryPredictions = useMemo(() => {
    if (!predicaoAtual?.todas_probabilidades) return [];
    return Object.entries(predicaoAtual.todas_probabilidades)
      .filter(([emocao]) => emocao !== predicaoAtual.emocao_principal)
      .map(([emocao, score]) => ({ label: emocao, score }))
      .sort((a, b) => parseFloat(b.score) - parseFloat(a.score))
      .slice(0, 4);
  }, [predicaoAtual]);

  const imagemResultado = predicaoAtual ? historico[0]?.url_imagem : null;
  const emocaoPrincipal = predicaoAtual ? predicaoAtual.emocao_principal : null;
  const certezaPrincipal = predicaoAtual ? predicaoAtual.certeza_principal : null;

  const getEmotionColors = (emotion: string | null) => {
    if (!emotion) return { color: 'var(--primary)', bg: 'linear-gradient(to right, var(--primary), var(--secondary))' };
    
    const lower = emotion.toLowerCase();
    switch(lower) {
      case 'happy': return { color: '#fbbf24', bg: '#fbbf24' };
      case 'angry': return { color: '#ef4444', bg: '#ef4444' };
      case 'fear': return { color: '#ffffff', bg: '#ffffff' };
      case 'neutral': return { color: '#6b7280', bg: '#6b7280' };
      case 'sad': return { color: '#3b82f6', bg: '#3b82f6' };
      case 'disgusted': return { color: '#22c55e', bg: '#22c55e' };
      case 'surprise': return { color: 'var(--primary)', bg: 'linear-gradient(to right, var(--primary), var(--secondary))' };
      case 'nenhum rosto humano detectado na imagem.': return { color: '#ff7a7a', bg: '#ff7a7a' };
      default: return { color: 'var(--primary)', bg: 'linear-gradient(to right, var(--primary), var(--secondary))' };
    }
  };

  const primaryColors = getEmotionColors(emocaoPrincipal);

  return (
    <div className="app-wrapper">
      <main className="main-container">

        {/* Hero */}
        <section className="hero-section">
          <h1 className="hero-title">
            Analise suas{' '}
            <span className="text-gradient">Emoções</span>
          </h1>
          <p className="hero-subtitle">
            Garanta de forma gratuita uma análise das emoções de suas fotos <br></br>por Redes Neurais feitas com PyTorch e OpenCV
          </p>
        </section>

        {/* Upload — linha horizontal */}
        <div className="upload-area">
          <div 
            className="upload-card"
            style={previewUrl ? { backgroundImage: `url(${previewUrl})`, backgroundSize: 'cover', backgroundPosition: 'center', position: 'relative' } : {}}
          >
            {previewUrl && <div className="upload-overlay" />}
            <div className="upload-content-stack">
              <div className="upload-meta">
                <p className="upload-title">
                  {selectedFile ? 'Imagem selecionada:' : 'Selecione uma imagem'}
                </p>
                <p className="upload-desc">
                  {selectedFile ? selectedFile.name : 'Selecione um arquivo ou use a câmera.'}
                </p>
                {erro && <p className="upload-error">{erro}</p>}
              </div>
              <div className="upload-actions">
                <input
                  id="file-input"
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                  onClick={(e) => { (e.target as HTMLInputElement).value = ''; }}
                />
                
                <div className="action-buttons-row">
                  <button
                    className="btn-icon-only"
                    type="button"
                    onClick={() => document.getElementById('file-input')?.click()}
                    disabled={loading}
                    title="Escolher Arquivo"
                  >
                    <FolderOpen size={18} />
                  </button>

                  <button
                    className="btn-icon-only"
                    type="button"
                    onClick={openCamera}
                    disabled={loading}
                    title="Ligar Câmera"
                  >
                    <Camera size={18} />
                  </button>

                  <button
                    className="btn-icon-only primary-action"
                    type="button"
                    onClick={() => void postImage()}
                    disabled={loading || !selectedFile}
                    title="Iniciar Análise"
                  >
                    {loading ? <Loader2 size={18} className="spinning-icon" /> : <Upload size={18} />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="results-section">
          <div className="glass-panel">
            {predicaoAtual?.status && (
              <div className={predicaoAtual.status === 'Erro' ? 'badge-error' : 'badge-active'}>
                {predicaoAtual.status === 'Erro' ? 'ERRO' : predicaoAtual.status}
              </div>
            )}
            <div className="analysis-content">
              <div className="preview-container">
                {imagemResultado
                  ? <img alt="Preview" className="preview-image" src={imagemResultado} />
                  : (
                    <div className="preview-placeholder">
                      <p style={{ color: 'var(--on-surface-variant)', fontSize: '0.65rem', textAlign: 'center', padding: '0.75rem' }}>
                        Sem imagem analizada
                      </p>
                    </div>
                  )
                }
              </div>
              <div className="data-area">
                <div>
                  <div className="classification-label">
                    <span className="label-text">Classificação por IA</span>
                    <span className="label-dot" />
                    <span className="label-text">Emoção Preedominante</span>
                  </div>
                  <h2 
                    className="emotion-title" 
                    style={{
                      color: predicaoAtual?.status === 'Erro' ? '#ff7a7a' : primaryColors.color, 
                      ...(predicaoAtual?.status === 'Erro' ? { fontSize: '1.25rem', lineHeight: '1.3' } : {})
                    }}
                  >
                    {emocaoPrincipal ?? 'Sem Análise'}
                  </h2>
                </div>
                <div>
                  <div className="score-header">
                    <span className="score-label">Nível de Acurácia</span>
                    <span 
                      className="score-value"
                      style={predicaoAtual?.status === 'Erro' ? { color: '#ff7a7a' } : {}}
                    >
                      {certezaPrincipal ?? '—'}
                    </span>
                  </div>
                  <div className="progress-track">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: certezaPrincipal ?? '0%',
                        background: predicaoAtual?.status === 'Erro' ? '#ff7a7a' : primaryColors.bg
                      }} 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Cards secundários — sempre renderizados se houver predição */}
          {predicaoAtual && (
            <div className="secondary-grid">
              {secondaryPredictions.length === 0 ? (
                <div className="prediction-card">
                  <div className="prediction-header">
                    <span className="prediction-label">Sem probabilidades secundárias</span>
                    <span className="prediction-score">—</span>
                  </div>
                </div>
              ) : (
                secondaryPredictions.map((item) => {
                  const secColors = getEmotionColors(item.label);
                  return (
                    <div key={item.label} className="prediction-card">
                      <div className="prediction-header">
                        <span className="prediction-label" style={{ color: secColors.color }}>{item.label}</span>
                        <span className="prediction-score">{item.score}</span>
                      </div>
                      <div className="mini-progress-track">
                        <div className="mini-progress-fill" style={{ width: item.score, background: secColors.bg }} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* History */}
        <section className="history-section">
          <div className="history-header">
            <div className="history-divider" />
            <h3 className="history-title">Histórico Recente de Análises</h3>
            <div className="history-divider" />
          </div>
          <div className="history-carousel">
            {historico.slice(0, 4).map((session) => {
              const histColors = getEmotionColors(session.emocao);
              return (
                <div key={session.id} className="history-card">
                  <div className="history-card-inner">
                    <img className="history-img" src={session.url_imagem} alt={session.emocao} />
                    <div className="history-text-container">
                      <p className="history-emotion" title={session.emocao} style={{ color: histColors.color }}>
                        {session.emocao}
                      </p>
                      <p className="history-time" title={session.data_hora}>{session.data_hora}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="btn-outline-wrapper" style={{ display: 'flex', gap: '0.8rem', justifyContent: 'center' }}>
            <button className="btn-outline" onClick={() => setIsModalOpen(true)}>
              <History size={13} />
              <span className="btn-outline-text">Histórico Completo</span>
            </button>
            <button 
              className="btn-outline btn-delete" 
              onClick={() => void deleteHistorico()} 
              title="Deletar Histórico"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </section>

      </main>

      {/* MODAL CÂMERA */}
      {isCameraOpen && (
        <div className="modal-overlay" onClick={closeCamera}>
          <div className="modal-content camera-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Câmera</h3>
              <button className="modal-close" onClick={closeCamera}>
                <X size={20} />
              </button>
            </div>
            <div className="camera-body">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                muted 
                className="camera-video-stream"
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
            <div className="camera-footer">
              <button className="btn-camera-capture" onClick={takePhoto}>
                <Camera size={20} />
                <span>Tirar Foto</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Histórico de Análise Completo</h2>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-history-list">
                {historico.map((session) => {
                  const histColors = getEmotionColors(session.emocao);
                  return (
                    <div key={session.id} className="history-card modal-history-card">
                      <div className="history-card-inner">
                        <img className="history-img" src={session.url_imagem} alt={session.emocao} />
                        <div className="history-text-container">
                          <p className="history-emotion" title={session.emocao} style={{ color: histColors.color }}>
                            {session.emocao}
                          </p>
                          <p className="history-time" title={session.data_hora}>{session.data_hora}</p>
                        </div>
                      </div>
                      <div className="modal-history-score" style={{ color: histColors.color }}>
                        {session.certeza ?? '0%'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}