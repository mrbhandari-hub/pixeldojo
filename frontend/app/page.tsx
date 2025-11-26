'use client';

import { useState, useRef, useEffect } from 'react';
import { Upload, Play, Download, Loader2, Image as ImageIcon, Sparkles, Wand2, Film, Zap } from 'lucide-react';

const API_URL = 'http://localhost:8001';

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('show them dancing');
  const [duration, setDuration] = useState(5);
  const [fastMode, setFastMode] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const statusIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, []);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const loadSampleImage = async () => {
    try {
      const response = await fetch('/test_image.png');
      const blob = await response.blob();
      const file = new File([blob], 'test_image.png', { type: 'image/png' });
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error loading sample image:', error);
      alert('Failed to load sample image');
    }
  };

  const pollStatus = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/status/${id}`);
      const data = await response.json();

      setProgress(data.progress || 0);
      setMessage(data.message || '');

      if (data.status === 'completed') {
        setStatus('completed');
        setVideoUrl(`${API_URL}/video/${id}`);
        if (statusIntervalRef.current) {
          clearInterval(statusIntervalRef.current);
        }
      } else if (data.status === 'failed') {
        setStatus('failed');
        if (statusIntervalRef.current) {
          clearInterval(statusIntervalRef.current);
        }
      }
    } catch (error) {
      console.error('Error polling status:', error);
    }
  };

  const handleGenerate = async () => {
    if (!image || !prompt.trim()) {
      alert('Please select an image and enter a prompt');
      return;
    }

    setStatus('processing');
    setProgress(0);
    setMessage('Initializing magic...');
    setVideoUrl(null);

    const formData = new FormData();
    formData.append('image', image);
    formData.append('prompt', prompt);
    formData.append('duration', duration.toString());
    formData.append('fast_mode', fastMode.toString());

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Generation failed');
      }

      const data = await response.json();
      setJobId(data.job_id);

      // Start polling for status
      statusIntervalRef.current = setInterval(() => {
        pollStatus(data.job_id);
      }, 2000);

      // Poll immediately
      pollStatus(data.job_id);
    } catch (error) {
      console.error('Error generating video:', error);
      setStatus('failed');
      setMessage('Failed to start generation');
    }
  };

  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `pixeldojo_${jobId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen text-slate-200 selection:bg-purple-500/30">
      <div className="container mx-auto px-4 py-12 max-w-6xl">

        {/* Header */}
        <header className="text-center mb-16 animate-float">
          <div className="inline-flex items-center justify-center p-3 mb-4 rounded-full glass-panel bg-purple-500/10 border-purple-500/20">
            <Sparkles className="w-6 h-6 text-purple-400 mr-2" />
            <span className="text-purple-300 font-medium tracking-wide text-sm uppercase">AI Video Studio</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 drop-shadow-lg">
            PixelDojo
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Transform your static images into mesmerizing video clips using state-of-the-art AI.
            <span className="block mt-2 text-slate-500 text-sm">Powered by ComfyUI & Wan2.2</span>
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Left Column: Controls */}
          <div className="lg:col-span-5 space-y-6">

            {/* Image Upload Card */}
            <div className="glass-panel rounded-2xl p-6 transition-all duration-300 hover:shadow-[0_0_30px_rgba(168,85,247,0.15)]">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <ImageIcon className="w-5 h-5 text-blue-400" />
                  Source Image
                </h2>
                {image && (
                  <button
                    onClick={() => {
                      setImage(null);
                      setImagePreview(null);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                    className="text-xs text-red-400 hover:text-red-300 transition-colors"
                  >
                    Remove
                  </button>
                )}
              </div>

              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => !image && fileInputRef.current?.click()}
                className={`
                  relative group cursor-pointer rounded-xl border-2 border-dashed transition-all duration-300 overflow-hidden
                  ${imagePreview
                    ? 'border-transparent h-64'
                    : 'border-slate-700 hover:border-purple-500/50 hover:bg-slate-800/50 h-48 flex flex-col items-center justify-center'
                  }
                `}
              >
                {imagePreview ? (
                  <>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <p className="text-white font-medium">Click to change</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                      <Upload className="w-6 h-6 text-slate-400 group-hover:text-purple-400" />
                    </div>
                    <p className="text-slate-400 font-medium group-hover:text-slate-200">Upload or drop image</p>
                    <p className="text-xs text-slate-600 mt-1">JPG, PNG, WebP</p>
                  </>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                />
              </div>

              {!image && (
                <button
                  onClick={loadSampleImage}
                  className="mt-3 w-full py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Use Sample Image
                </button>
              )}
            </div>

            {/* Settings Card */}
            <div className="glass-panel rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Wand2 className="w-5 h-5 text-purple-400" />
                Generation Settings
              </h2>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Prompt</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe the motion and atmosphere..."
                    className="w-full h-32 p-4 glass-input rounded-xl resize-none focus:outline-none text-sm placeholder:text-slate-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <label className="text-slate-400">Duration</label>
                    <span className="text-purple-400 font-mono">{duration}s</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="60"
                    step="5"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                  />
                  <div className="flex justify-between text-xs text-slate-600 mt-1">
                    <span>5s</span>
                    <span>60s</span>
                  </div>
                </div>

                {/* Fast Mode Toggle */}
                <div className="pt-2 border-t border-slate-800">
                  <button
                    onClick={() => setFastMode(!fastMode)}
                    className={`
                      w-full py-3 px-4 rounded-xl font-medium text-sm transition-all duration-300 flex items-center justify-between
                      ${fastMode 
                        ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-300' 
                        : 'bg-slate-800/50 border border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-300'
                      }
                    `}
                  >
                    <div className="flex items-center gap-2">
                      <Zap className={`w-4 h-4 ${fastMode ? 'text-amber-400' : 'text-slate-500'}`} />
                      <span>Fast Mode</span>
                    </div>
                    <div className={`
                      w-10 h-5 rounded-full transition-all duration-300 relative
                      ${fastMode ? 'bg-amber-500' : 'bg-slate-700'}
                    `}>
                      <div className={`
                        absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-300
                        ${fastMode ? 'left-5' : 'left-0.5'}
                      `} />
                    </div>
                  </button>
                  <p className="text-xs text-slate-600 mt-2 text-center">
                    {fastMode ? '⚡ ~3x faster • 15 steps, FP8, lower res' : 'Standard quality • ~4-5 min per clip'}
                  </p>
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={status === 'processing' || !image || !prompt.trim()}
              className={`
                w-full py-4 px-6 rounded-xl font-bold text-lg tracking-wide shadow-lg transition-all duration-300
                flex items-center justify-center gap-3
                ${status === 'processing' || !image || !prompt.trim()
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-purple-500/25 hover:shadow-purple-500/40 hover:-translate-y-0.5'
                }
              `}
            >
              {status === 'processing' ? (
                <>
                  <Loader2 className="animate-spin h-6 w-6" />
                  Generating Magic...
                </>
              ) : (
                <>
                  <Play className="h-6 w-6 fill-current" />
                  Generate Video
                </>
              )}
            </button>
          </div>

          {/* Right Column: Output */}
          <div className="lg:col-span-7">
            <div className="glass-panel rounded-2xl p-1 h-full min-h-[600px] flex flex-col relative overflow-hidden">

              {/* Status Overlay */}
              {status === 'processing' && (
                <div className="absolute inset-0 z-20 bg-slate-900/80 backdrop-blur-sm flex flex-col items-center justify-center p-8">
                  <div className="w-full max-w-md space-y-4 text-center">
                    <div className="relative w-24 h-24 mx-auto mb-6">
                      <div className="absolute inset-0 rounded-full border-4 border-slate-700"></div>
                      <div className="absolute inset-0 rounded-full border-4 border-t-purple-500 border-r-blue-500 border-b-transparent border-l-transparent animate-spin"></div>
                      <Sparkles className="absolute inset-0 m-auto w-8 h-8 text-white animate-pulse" />
                    </div>
                    <h3 className="text-2xl font-bold text-white">Creating your masterpiece</h3>
                    <p className="text-slate-400">{message}</p>

                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mt-8">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-slate-500 font-mono">{progress}% Complete</p>
                  </div>
                </div>
              )}

              {/* Video Player or Placeholder */}
              <div className="flex-1 bg-slate-950 rounded-xl overflow-hidden relative group">
                {status === 'completed' && videoUrl ? (
                  <div className="w-full h-full flex flex-col">
                    <video
                      src={videoUrl}
                      controls
                      autoPlay
                      loop
                      className="w-full h-full object-contain bg-black"
                    />
                  </div>
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 p-8 text-center">
                    <div className="w-24 h-24 rounded-full bg-slate-900/50 flex items-center justify-center mb-6 border border-slate-800">
                      <Film className="w-10 h-10 opacity-50" />
                    </div>
                    <h3 className="text-xl font-medium text-slate-400 mb-2">Ready to Create</h3>
                    <p className="text-sm max-w-xs mx-auto">
                      Upload an image and describe your vision to generate a stunning video clip.
                    </p>
                  </div>
                )}
              </div>

              {/* Download Action */}
              {status === 'completed' && videoUrl && (
                <div className="p-6 bg-slate-900/50 border-t border-white/5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-medium">Generation Complete</h3>
                      <p className="text-sm text-slate-400">Your video is ready to download</p>
                    </div>
                    <button
                      onClick={handleDownload}
                      className="bg-white text-slate-900 hover:bg-slate-200 px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-colors"
                    >
                      <Download className="w-5 h-5" />
                      Download
                    </button>
                  </div>
                </div>
              )}

              {/* Error State */}
              {status === 'failed' && (
                <div className="absolute inset-0 z-20 bg-slate-900/90 backdrop-blur-md flex flex-col items-center justify-center p-8">
                  <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4 border border-red-500/20">
                    <span className="text-2xl">⚠️</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Generation Failed</h3>
                  <p className="text-red-400 mb-6 text-center max-w-md">{message}</p>
                  <button
                    onClick={() => setStatus('idle')}
                    className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
