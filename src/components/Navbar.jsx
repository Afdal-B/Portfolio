import React from "react";
import logo from "../assets/my-logo.png";
import { FaLinkedin } from "react-icons/fa";
import { FaGithub } from "react-icons/fa";
import { FaInstagram } from "react-icons/fa";
const Navbar = () => {
  return (
    <nav className="mb-20 flex items-center justify-between py-6 ">
      <div>
        <img className="mx-2 w-10" src={logo} alt="logo" />
      </div>
      <div className="m-8 flex items-center justify-center gap-4">
        <a href="https://www.linkedin.com/in/afdal-bouraima-276183253/">
          <FaLinkedin></FaLinkedin>
        </a>
        <a href="https://github.com/Afdal-B">
          <FaGithub></FaGithub>
        </a>
        <a href="https://www.instagram.com/dalfa_ad_astra/?hl=fr">
          <FaInstagram></FaInstagram>
        </a>
      </div>
    </nav>
  );
};

export default Navbar;
