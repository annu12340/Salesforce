import { useEffect, useState } from 'react';

export const Background = () => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="fixed inset-0 z-0 overflow-hidden">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/10 to-black/30 z-10" />
      
      {/* Animated circles */}
      <div className={`absolute top-20 right-20 w-64 h-64 rounded-full bg-blue-500/20 blur-3xl ${mounted ? 'fade-in' : 'opacity-0'}`} 
           style={{ animationDelay: '0.2s' }} />
      <div className={`absolute bottom-40 left-20 w-80 h-80 rounded-full bg-purple-500/20 blur-3xl ${mounted ? 'fade-in' : 'opacity-0'}`}
           style={{ animationDelay: '0.5s' }} />
      <div className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-indigo-500/10 blur-3xl ${mounted ? 'fade-in' : 'opacity-0'}`}
           style={{ animationDelay: '0.8s' }} />
    </div>
  );
}; 