import React from "react";
import Project from "./Project";
import { motion } from "framer-motion";
function Projects() {
  return (
    <div className="border-b border-neutral-800 pb-24">
      <motion.h2
        initial={{ y: -100, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="my-20 text-center text-4xl"
      >
        Projects
      </motion.h2>
      <motion.div
        initial={{ x: -100, opacity: 0 }}
        whileInView={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex flex-wrap items-center justify-center lg:flex-nowrap gap-5"
      >
        <Project
          title="Compiler"
          toolslist="Java JFlex CUP"
          github="https://github.com/Afdal-B/Compilation"
        />

        <Project
          title="Responsive Disney+ clone"
          toolslist="React tailwindCSS TMDB"
          github="https://github.com/Afdal-B/Disney-Clone"
          link="https://disney-clone-delta-lilac.vercel.app"
        />
      </motion.div>
    </div>
  );
}

export default Projects;
