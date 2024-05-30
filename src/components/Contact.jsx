import React from "react";
import { IoIosMail } from "react-icons/io";
import { motion } from "framer-motion";

function Contact() {
  return (
    <div className="border-b border-neutral-900 pb-4 lg:mb-35">
      <motion.h2
        initial={{ y: -100, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="my-20 text-center text-4xl"
      >
        Contact Me
      </motion.h2>
      <div className="flex flex-wrap">
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex w-full lg:w-1/2 justify-center"
        >
          <IoIosMail className="text-10xl" />
        </motion.div>
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          whileInView={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex w-full lg:w-1/2 justify-center"
        >
          <form
            action="https://api.web3forms.com/submit"
            method="POST"
            className="flex flex-col w-full lg:w-3/4  space-y-4"
          >
            <input
              type="hidden"
              name="access_key"
              value="838183f5-d240-4ec8-b13c-1d90bcff3e1d"
            />

            <input
              type="text"
              name="name"
              id="name"
              required
              placeholder="Name"
              className="p-4 border border-gray-300 rounded-3xl bg-black"
            />

            <input
              type="email"
              name="email"
              id="email"
              required
              placeholder="Email"
              className="p-4 border border-gray-300 rounded-3xl bg-black"
            />

            <textarea
              name="message"
              id="message"
              cols="40"
              rows="8"
              placeholder="Message"
              className="p-4 border border-gray-300 rounded-3xl bg-black"
            ></textarea>
            <button className="px-4 py-2 bg-green-800 text-white rounded-3xl">
              Submit
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}

export default Contact;
