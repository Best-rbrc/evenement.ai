import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Sparkles, Zap, Brain, Calendar, Users, Rocket, ArrowRight, Star, Hexagon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';
import { FeatureCard } from '@/components/FeatureCard';
import { useEffect, useState, useRef } from 'react';

interface LandingPageProps {
  onGetStarted: () => void;
}

// Floating particle component
const Particle = ({ delay, duration, size, x, y }: { delay: number; duration: number; size: number; x: number; y: number }) => (
  <motion.div
    className="absolute rounded-full bg-gradient-to-r from-soft-coral/40 to-rose-gold/40 blur-sm"
    style={{ width: size, height: size, left: `${x}%`, top: `${y}%` }}
    animate={{
      y: [0, -100, 0],
      x: [0, 30, -20, 0],
      scale: [1, 1.2, 0.8, 1],
      opacity: [0.3, 0.7, 0.3],
    }}
    transition={{
      duration,
      delay,
      repeat: Infinity,
      ease: "easeInOut",
    }}
  />
);

// Animated orb component
const FloatingOrb = ({ className, delay = 0 }: { className?: string; delay?: number }) => (
  <motion.div
    className={`absolute rounded-full blur-3xl ${className}`}
    animate={{
      scale: [1, 1.2, 1],
      rotate: [0, 180, 360],
      x: [0, 50, -30, 0],
      y: [0, -30, 20, 0],
    }}
    transition={{
      duration: 20,
      delay,
      repeat: Infinity,
      ease: "linear",
    }}
  />
);

// 3D Card component
const Card3D = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const rotateX = useSpring(useTransform(y, [-100, 100], [15, -15]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(x, [-100, 100], [-15, 15]), { stiffness: 300, damping: 30 });

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
  };

  return (
    <motion.div
      ref={ref}
      className={className}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      onMouseMove={handleMouse}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </motion.div>
  );
};

// Glowing text component
const GlowText = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <span className={`relative ${className}`}>
    <span className="absolute inset-0 blur-2xl bg-gradient-to-r from-soft-coral to-rose-gold opacity-50" />
    <span className="relative">{children}</span>
  </span>
);

// Animated counter
const AnimatedCounter = ({ target, suffix = "" }: { target: number; suffix?: string }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    
    return () => clearInterval(timer);
  }, [target]);
  
  return <span>{count.toLocaleString()}{suffix}</span>;
};

// Agent icon with pulse effect
const AgentIcon = ({ icon: Icon, label, delay }: { icon: typeof Brain; label: string; delay: number }) => (
  <motion.div
    className="flex flex-col items-center gap-2"
    initial={{ opacity: 0, scale: 0 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, type: "spring", stiffness: 200 }}
  >
    <motion.div
      className="relative w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-gradient-to-br from-soft-coral/20 to-rose-gold/20 border border-border/50 flex items-center justify-center backdrop-blur-sm"
      whileHover={{ scale: 1.1, rotate: 5 }}
      animate={{
        boxShadow: [
          "0 0 20px rgba(249, 115, 22, 0.2)",
          "0 0 40px rgba(249, 115, 22, 0.4)",
          "0 0 20px rgba(249, 115, 22, 0.2)",
        ],
      }}
      transition={{ duration: 2, repeat: Infinity }}
    >
      <Icon className="w-8 h-8 md:w-10 md:h-10 text-soft-coral" />
      <motion.div
        className="absolute inset-0 rounded-2xl border-2 border-soft-coral/50"
        animate={{ scale: [1, 1.2, 1], opacity: [1, 0, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: delay * 0.5 }}
      />
    </motion.div>
    <span className="text-xs md:text-sm text-muted-foreground font-medium">{label}</span>
  </motion.div>
);

// Neural network animation
const NeuralNetwork = () => {
  const nodes = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: 10 + (i % 4) * 30,
    y: 20 + Math.floor(i / 4) * 30,
  }));

  return (
    <svg className="absolute inset-0 w-full h-full opacity-20" viewBox="0 0 100 100">
      {nodes.map((node, i) =>
        nodes.slice(i + 1).map((target, j) => (
          <motion.line
            key={`${i}-${j}`}
            x1={node.x}
            y1={node.y}
            x2={target.x}
            y2={target.y}
            stroke="url(#gradient)"
            strokeWidth="0.3"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: [0, 0.5, 0] }}
            transition={{
              duration: 3,
              delay: (i + j) * 0.1,
              repeat: Infinity,
              repeatDelay: 2,
            }}
          />
        ))
      )}
      {nodes.map((node) => (
        <motion.circle
          key={node.id}
          cx={node.x}
          cy={node.y}
          r="1.5"
          fill="url(#gradient)"
          initial={{ scale: 0 }}
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ duration: 2, repeat: Infinity, delay: node.id * 0.1 }}
        />
      ))}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="hsl(var(--soft-coral))" />
          <stop offset="100%" stopColor="hsl(var(--rose-gold))" />
        </linearGradient>
      </defs>
    </svg>
  );
};

// Hexagon grid background
const HexGrid = () => (
  <div className="absolute inset-0 overflow-hidden opacity-10">
    {Array.from({ length: 20 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute"
        style={{
          left: `${(i % 5) * 25}%`,
          top: `${Math.floor(i / 5) * 25}%`,
        }}
        initial={{ opacity: 0, rotate: 0 }}
        animate={{ opacity: [0.2, 0.5, 0.2], rotate: 360 }}
        transition={{ duration: 20, delay: i * 0.5, repeat: Infinity }}
      >
        <Hexagon className="w-32 h-32 text-soft-coral" strokeWidth={0.5} />
      </motion.div>
    ))}
  </div>
);

export const LandingPage = ({ onGetStarted }: LandingPageProps) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const particles = Array.from({ length: 30 }, (_, i) => ({
    delay: i * 0.3,
    duration: 8 + Math.random() * 4,
    size: 4 + Math.random() * 12,
    x: Math.random() * 100,
    y: Math.random() * 100,
  }));

  const features = [
    { icon: Brain, title: "12 Agents & 1 Coordinator", description: "Specialized agents for every aspect of event planning" },
    { icon: Zap, title: "Real-time Processing", description: "Watch your event plan come together live" },
    { icon: Calendar, title: "Complete Plans", description: "From venue to catering to entertainment" },
    { icon: Users, title: "Guest Management", description: "Handle events from 10 to 10,000 attendees" },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background effects */}
      <div className="fixed inset-0 gradient-hero transition-colors duration-500" />
      
      {/* Mouse follower gradient */}
      <motion.div
        className="fixed w-[600px] h-[600px] rounded-full bg-gradient-radial from-soft-coral/20 via-transparent to-transparent blur-3xl pointer-events-none"
        animate={{ x: mousePosition.x - 300, y: mousePosition.y - 300 }}
        transition={{ type: "spring", damping: 30, stiffness: 200 }}
      />

      {/* Floating orbs */}
      <FloatingOrb className="w-96 h-96 bg-soft-coral/20 -top-48 -left-48" />
      <FloatingOrb className="w-[500px] h-[500px] bg-rose-gold/15 -bottom-64 -right-64" delay={5} />
      <FloatingOrb className="w-72 h-72 bg-lavender-mist/30 top-1/3 right-1/4" delay={10} />

      {/* Particles */}
      <div className="fixed inset-0 pointer-events-none">
        {particles.map((p, i) => (
          <Particle key={i} {...p} />
        ))}
      </div>

      {/* Hex grid */}
      <HexGrid />

      {/* Header with Theme Toggle */}
      <motion.header
        className="fixed top-0 left-0 right-0 z-50 px-4 py-4"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div 
            className="flex items-center gap-3 group"
            whileHover={{ scale: 1.02 }}
          >
            <motion.div
              className="relative w-12 h-12 flex items-center justify-center"
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              {/* Custom logo - stylized "E" with event elements */}
              <svg 
                viewBox="0 0 40 40" 
                className="w-12 h-12 group-hover:scale-105 transition-transform drop-shadow-lg"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* Background circle with gradient */}
                <defs>
                  <linearGradient id="logoGradientLanding" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#E67E5A" />
                    <stop offset="100%" stopColor="#D4A574" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <circle cx="20" cy="20" r="18" fill="url(#logoGradientLanding)" filter="url(#glow)" />
                
                {/* Stylized "E" letter */}
                <path 
                  d="M12 10 L12 30 M12 10 L28 10 M12 20 L24 20 M12 30 L28 30" 
                  stroke="white" 
                  strokeWidth="2.5" 
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                
                {/* Decorative event dots */}
                <circle cx="26" cy="14" r="2" fill="white" opacity="0.9">
                  <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite" />
                  <animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="26" cy="26" r="2" fill="white" opacity="0.9">
                  <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" begin="0.5s" repeatCount="indefinite" />
                  <animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="2s" begin="0.5s" repeatCount="indefinite" />
                </circle>
              </svg>
            </motion.div>
            <span className="text-2xl font-display font-bold text-foreground">
              Évènement.ai
            </span>
          </motion.div>
          
          <ThemeToggle />
        </div>
      </motion.header>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex flex-col items-center justify-center px-4 py-20">
          <motion.div
            className="text-center max-w-5xl mx-auto"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border mb-8"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4 text-soft-coral" />
              </motion.div>
              <span className="text-sm font-medium">Powered by 12 agents and 1 coordinator</span>
            </motion.div>

            {/* Main heading */}
            <motion.h1
              className="text-5xl md:text-7xl lg:text-8xl font-display font-bold mb-6 leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <span className="block">Plan Events with</span>
              <GlowText className="bg-gradient-to-r from-soft-coral via-rose-gold to-lavender-mist bg-clip-text text-transparent">
                AI Superpowers
              </GlowText>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto mb-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              From corporate conferences to dream weddings, watch 12 specialized AI agents
              create your perfect event plan in real-time.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Button
                size="lg"
                className="group relative overflow-hidden text-lg px-8 py-6 bg-gradient-to-r from-soft-coral to-rose-gold hover:shadow-glow transition-all duration-300"
                onClick={onGetStarted}
              >
                <motion.span
                  className="absolute inset-0 bg-white/20"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: "100%" }}
                  transition={{ duration: 0.5 }}
                />
                <span className="relative flex items-center gap-2">
                  Start Planning
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="w-5 h-5" />
                  </motion.span>
                </span>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-6 glass-panel hover:bg-background/50"
                onClick={() => window.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '_blank')}
              >
                <Rocket className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </motion.div>
          </motion.div>

          {/* Agent icons showcase */}
          <motion.div
            className="mt-20 flex flex-wrap justify-center gap-6 max-w-4xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            <AgentIcon icon={Brain} label="Venue" delay={1.1} />
            <AgentIcon icon={Zap} label="Budget" delay={1.2} />
            <AgentIcon icon={Calendar} label="Schedule" delay={1.3} />
            <AgentIcon icon={Users} label="Speakers" delay={1.4} />
            <AgentIcon icon={Star} label="Catering" delay={1.5} />
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-6 h-10 rounded-full border-2 border-border/50 flex items-start justify-center p-2">
              <motion.div
                className="w-1.5 h-1.5 rounded-full bg-soft-coral"
                animate={{ y: [0, 16, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
          </motion.div>
        </section>

        {/* Stats Section */}
        <section className="py-20 px-4 relative">
          <div className="max-w-6xl mx-auto">
            <motion.div
              className="grid grid-cols-2 md:grid-cols-4 gap-8"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              {[
                { value: 12, suffix: "", label: "AI Agents" },
                { value: 50000, suffix: "+", label: "Events Planned" },
                { value: 99, suffix: "%", label: "Success Rate" },
                { value: 24, suffix: "/7", label: "Availability" },
              ].map((stat, i) => (
                <Card3D key={i} className="perspective-1000">
                  <div className="glass-panel p-6 rounded-2xl border text-center">
                    <div className="text-3xl md:text-5xl font-display font-bold bg-gradient-to-r from-soft-coral to-rose-gold bg-clip-text text-transparent mb-2">
                      <AnimatedCounter target={stat.value} suffix={stat.suffix} />
                    </div>
                    <div className="text-muted-foreground font-medium">{stat.label}</div>
                  </div>
                </Card3D>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4 relative">
          <NeuralNetwork />
          <div className="max-w-6xl mx-auto relative z-10">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">
                Why Choose <GlowText className="text-soft-coral">Évènement.ai</GlowText>?
              </h2>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Our multi-agent system handles every aspect of event planning with precision and creativity.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {features.map((feature, i) => (
                <FeatureCard
                  key={i}
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                  index={i}
                />
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 relative">
          <div className="max-w-4xl mx-auto">
            <motion.div
              className="glass-panel p-12 rounded-3xl border text-center relative overflow-hidden"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
            >
              {/* Animated background */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-soft-coral/10 via-rose-gold/10 to-lavender-mist/10"
                animate={{
                  backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                }}
                transition={{ duration: 10, repeat: Infinity }}
                style={{ backgroundSize: "200% 200%" }}
              />

              <div className="relative z-10">
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block mb-6"
                >
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-soft-coral to-rose-gold flex items-center justify-center shadow-glow">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                </motion.div>

                <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
                  Ready to Plan Your Perfect Event?
                </h2>
                <p className="text-muted-foreground text-lg mb-8 max-w-xl mx-auto">
                  Join thousands of event planners who trust our AI agents to create unforgettable experiences.
                </p>

                <Button
                  size="lg"
                  className="text-lg px-10 py-6 bg-gradient-to-r from-soft-coral to-rose-gold hover:shadow-glow transition-all duration-300"
                  onClick={onGetStarted}
                >
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 px-4 border-t border-border/50">
          <div className="max-w-6xl mx-auto text-center text-muted-foreground">
            <p>© 2025 Évènement.ai. Powered by 12 agents and 1 coordinator • Built with love and a lot of pain</p>
          </div>
        </footer>
      </div>
    </div>
  );
};
