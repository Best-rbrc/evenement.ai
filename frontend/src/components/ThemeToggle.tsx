import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

export const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);
  }, []);

  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    
    if (newIsDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-14 h-14 rounded-2xl glass-panel border border-border/50 flex items-center justify-center overflow-hidden group"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Background glow effect */}
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background: isDark 
            ? 'radial-gradient(circle, hsl(var(--lavender-mist) / 0.3) 0%, transparent 70%)'
            : 'radial-gradient(circle, hsl(var(--soft-coral) / 0.3) 0%, transparent 70%)',
        }}
      />

      {/* Animated stars for dark mode */}
      <AnimatePresence>
        {isDark && (
          <>
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full bg-lavender-mist"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ 
                  opacity: [0, 1, 0],
                  scale: [0, 1, 0],
                }}
                exit={{ opacity: 0, scale: 0 }}
                transition={{
                  duration: 2,
                  delay: i * 0.3,
                  repeat: Infinity,
                }}
                style={{
                  left: `${20 + i * 25}%`,
                  top: `${15 + i * 20}%`,
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>

      {/* Animated sun rays */}
      <AnimatePresence>
        {!isDark && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-0.5 h-3 bg-gradient-to-t from-soft-coral/50 to-transparent rounded-full"
                style={{
                  transformOrigin: 'center 20px',
                  rotate: `${i * 45}deg`,
                }}
                animate={{
                  opacity: [0.3, 0.7, 0.3],
                  scaleY: [0.8, 1.2, 0.8],
                }}
                transition={{
                  duration: 2,
                  delay: i * 0.1,
                  repeat: Infinity,
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Icon container with 3D flip */}
      <motion.div
        className="relative z-10"
        animate={{ rotateY: isDark ? 180 : 0 }}
        transition={{ duration: 0.6, type: "spring", stiffness: 200 }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <AnimatePresence mode="wait">
          {isDark ? (
            <motion.div
              key="moon"
              initial={{ opacity: 0, rotate: -90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 90 }}
              transition={{ duration: 0.3 }}
            >
              <Moon className="w-6 h-6 text-lavender-mist" />
            </motion.div>
          ) : (
            <motion.div
              key="sun"
              initial={{ opacity: 0, rotate: 90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: -90 }}
              transition={{ duration: 0.3 }}
            >
              <Sun className="w-6 h-6 text-soft-coral" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Ripple effect on click */}
      <motion.div
        className="absolute inset-0 rounded-2xl"
        initial={{ scale: 0, opacity: 0.5 }}
        whileTap={{ scale: 2, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          background: isDark 
            ? 'radial-gradient(circle, hsl(var(--soft-coral)) 0%, transparent 70%)'
            : 'radial-gradient(circle, hsl(var(--lavender-mist)) 0%, transparent 70%)',
        }}
      />
    </motion.button>
  );
};
