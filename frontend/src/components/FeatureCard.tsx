import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { useRef, useState } from 'react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  index: number;
}

export const FeatureCard = ({ icon: Icon, title, description, index }: FeatureCardProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const rotateX = useSpring(useTransform(y, [-100, 100], [10, -10]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(x, [-100, 100], [-10, 10]), { stiffness: 300, damping: 30 });

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set(e.clientX - centerX);
    y.set(e.clientY - centerY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
    setIsHovered(false);
  };

  // Different accent colors for each card
  const accents = [
    { from: 'from-soft-coral', to: 'to-rose-gold', glow: 'hsl(var(--soft-coral))' },
    { from: 'from-lavender-mist', to: 'to-rose-gold', glow: 'hsl(var(--lavender-mist))' },
    { from: 'from-sage', to: 'to-deep-teal', glow: 'hsl(var(--sage))' },
    { from: 'from-gold', to: 'to-soft-coral', glow: 'hsl(var(--gold))' },
  ];
  
  const accent = accents[index % accents.length];

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      onMouseMove={handleMouse}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      className="h-full perspective-1000"
    >
      <motion.div
        className="glass-panel p-8 rounded-2xl border h-full relative overflow-hidden cursor-pointer"
        animate={{
          boxShadow: isHovered 
            ? `0 25px 50px -12px ${accent.glow}40, 0 0 30px ${accent.glow}20`
            : '0 4px 20px -2px rgba(0,0,0,0.06)',
        }}
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.3 }}
      >
        {/* Animated gradient border */}
        <motion.div
          className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${accent.from} ${accent.to} opacity-0`}
          animate={{ opacity: isHovered ? 0.1 : 0 }}
          transition={{ duration: 0.3 }}
        />

        {/* Shimmer effect on hover */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12"
          initial={{ x: '-200%' }}
          animate={{ x: isHovered ? '200%' : '-200%' }}
          transition={{ duration: 0.8, ease: 'easeInOut' }}
        />

        {/* Floating particles on hover */}
        {isHovered && (
          <>
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className={`absolute w-2 h-2 rounded-full bg-gradient-to-r ${accent.from} ${accent.to}`}
                initial={{ 
                  opacity: 0,
                  x: '50%',
                  y: '50%',
                  scale: 0
                }}
                animate={{ 
                  opacity: [0, 0.6, 0],
                  x: `${Math.random() * 100}%`,
                  y: `${Math.random() * 100}%`,
                  scale: [0, 1, 0]
                }}
                transition={{
                  duration: 1.5,
                  delay: i * 0.1,
                  repeat: Infinity,
                }}
              />
            ))}
          </>
        )}

        {/* Icon with enhanced animations */}
        <motion.div
          className={`relative w-16 h-16 rounded-xl bg-gradient-to-br ${accent.from}/20 ${accent.to}/20 flex items-center justify-center mb-5`}
          animate={{
            rotate: isHovered ? [0, -5, 5, 0] : 0,
          }}
          transition={{ duration: 0.5 }}
        >
          {/* Icon glow ring */}
          <motion.div
            className={`absolute inset-0 rounded-xl bg-gradient-to-br ${accent.from} ${accent.to}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: isHovered ? [0.3, 0.5, 0.3] : 0,
              scale: isHovered ? [1, 1.2, 1] : 0.8,
            }}
            transition={{ duration: 1.5, repeat: isHovered ? Infinity : 0 }}
          />
          
          {/* Orbiting dot */}
          {isHovered && (
            <motion.div
              className={`absolute w-2 h-2 rounded-full bg-gradient-to-r ${accent.from} ${accent.to}`}
              animate={{
                rotate: 360,
              }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              style={{ 
                x: 30,
                transformOrigin: '-22px center',
              }}
            />
          )}

          <motion.div
            animate={{ 
              scale: isHovered ? [1, 1.1, 1] : 1,
              rotate: isHovered ? [0, 10, -10, 0] : 0,
            }}
            transition={{ duration: 0.5 }}
          >
            <Icon className={`w-8 h-8 text-soft-coral relative z-10`} />
          </motion.div>
        </motion.div>

        {/* Title with gradient reveal */}
        <motion.h3 
          className="text-xl font-display font-bold mb-2 relative"
          animate={{
            color: isHovered ? accent.glow : 'inherit',
          }}
          transition={{ duration: 0.3 }}
        >
          {title}
          <motion.span
            className={`absolute bottom-0 left-0 h-0.5 bg-gradient-to-r ${accent.from} ${accent.to}`}
            initial={{ width: 0 }}
            animate={{ width: isHovered ? '100%' : 0 }}
            transition={{ duration: 0.3 }}
          />
        </motion.h3>

        {/* Description with stagger animation */}
        <motion.p 
          className="text-muted-foreground relative z-10"
          animate={{
            y: isHovered ? -2 : 0,
            opacity: isHovered ? 1 : 0.8,
          }}
          transition={{ duration: 0.3 }}
        >
          {description}
        </motion.p>

        {/* Corner accent */}
        <motion.div
          className={`absolute -bottom-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br ${accent.from}/20 ${accent.to}/20 blur-2xl`}
          animate={{
            scale: isHovered ? 1.5 : 1,
            opacity: isHovered ? 0.6 : 0.2,
          }}
          transition={{ duration: 0.5 }}
        />

        {/* Interactive cursor hint */}
        <motion.div
          className="absolute bottom-4 right-4 flex items-center gap-1 text-xs text-muted-foreground/50"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.span
            animate={{ x: [0, 3, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
          >
            →
          </motion.span>
          Explore
        </motion.div>
      </motion.div>
    </motion.div>
  );
};
