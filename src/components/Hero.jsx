import { motion, useScroll, useTransform } from "framer-motion";

const Hero = () => {
  const { scrollY } = useScroll();
  const opacity = useTransform(scrollY, [0, 100], [1, 0]);
  const translateY = useTransform(scrollY, [0, 100], [0, -20]);

  return (
    <section className="relative min-h-screen flex items-start justify-center overflow-hidden text-white pt-40 border-b border-neutral-800 pb-24">
      <div className="container mx-auto px-4 z-10 text-center">
        <div className="max-w-4xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-4xl md:text-7xl font-light mb-6 tracking-wider cinzel-decorative-regular"
          >
            Afdal Bouraima
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-xl md:text-2xl text-gray-400 mb-8 tracking-wide font-serif"
          >
            Software engineer
          </motion.p>
        </div>
      </div>

      <motion.div
        className="text-center absolute bottom-[10.5rem] -translate-x-[50%] text-sm text-gray-500"
        style={{ opacity, translateY }}
      >
        Scroll to discover
      </motion.div>
    </section>
  );
};

export default Hero;
