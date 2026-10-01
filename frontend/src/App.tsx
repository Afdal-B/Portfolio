import { Header } from "./components/header/Header"
import { Hero } from "./components/sections/Hero"
import { ProjectsSection } from "./components/sections/ProjectsSection"
import { ExperienceSection } from "./components/sections/ExperienceSection"
import { SkillsSection } from "./components/sections/SkillsSection"
import { AssistantSection } from "./components/sections/AssistantSection"
import { ContactFooter } from "./components/sections/ContactFooter"
import { ProjectModal } from "./components/modal/ProjectModal"

/** A classic, scannable page first (a recruiter in a hurry reads it top to
 *  bottom without typing anything), with the RAG assistant as one section of
 *  it rather than the whole interface. */
function App() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <Header />
      <main id="top">
        <Hero />
        <ProjectsSection />
        <ExperienceSection />
        <SkillsSection />
        <AssistantSection />
      </main>
      <ContactFooter />
      <ProjectModal />
    </div>
  )
}

export default App
