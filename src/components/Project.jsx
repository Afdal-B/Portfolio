import React from "react";
import { FaGithub } from "react-icons/fa";
import { FaLink } from "react-icons/fa";

const tools = (toolslist) => {
  const list = toolslist.split(" ");
  return list.map((tool) => <span>{tool}</span>);
};

function Project(props) {
  return (
    <div className="w-full lg:w-1/3 rounded-2xl border-4 border-neutral-800 p-4 flex flex-col">
      <div className="flex gap-4 flex-row-reverse p-1">
        <a href={props.github}>
          <FaGithub />
        </a>
        {props.link && (
          <a href={props.link}>
            <FaLink />
          </a>
        )}
      </div>

      <h3 className="text-center mt-6">{props.title}</h3>

      <div className="flex gap-4 justify-center content-center m-6">
        {tools(props.toolslist)}
      </div>
    </div>
  );
}

export default Project;
