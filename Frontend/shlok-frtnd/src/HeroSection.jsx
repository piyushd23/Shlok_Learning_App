import React from "react";



const services = [
  { name: "Android Development", icon: "\ud83d\udcbb" },
  { name: "Web Development", icon: "\ud83d\udcda" },
  { name: "UI/UX Design", icon: "\ud83c\udfa8" },
  { name: "Branding", icon: "\ud83c\udf10" },
  { name: "SaaS", icon: "\ud83d\udcbc" },
  { name: "Product Design", icon: "\ud83c\udf1f" },
];

const HeroSection = () => {
  return (
    <div className="font-montserrat bg-white text-black p-10 flex flex-col md:flex-row items-center justify-between">
      {/* Left Section */}
      <div className="md:w-1/2">
        <h1 className="text-4xl font-bold">We Build Brands, Not Just Websites.</h1>
        <h2 className="text-xl font-semibold mt-4">
          <span className="text-orange-500">Devlok Avenue</span> – Disrupt. Design. Dominate
        </h2>
        <p className="text-gray-600 mt-4">
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Saepe reiciendis
          perferendis veritatis dolores, dolorem praesentium atque quaerat, repudiandae
          fugit provident tenetur laborum dolore pariatur.
        </p>
        <div className="flex space-x-10 mt-6">
          <div className="text-center">
            <p className="text-3xl font-bold">100</p>
            <p className="text-gray-500">Happy Clients</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold">100</p>
            <p className="text-gray-500">Happy Clients</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold">100</p>
            <p className="text-gray-500">Happy Clients</p>
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="relative md:w-1/2 flex justify-center items-center mt-10 md:mt-0">
        <img src="D:\Shlok\Frontend\shlok-frtnd\decoration.png" alt="Decorative Background" className="w-full h-auto absolute" />
        {services.map((service, index) => (
          <div
            key={index}
            className="absolute bg-white shadow-md px-3 py-2 rounded-lg flex items-center text-sm font-medium"
            style={{
              top: `${30 + index * 10}%`,
              left: index % 2 === 0 ? "-20%" : "80%",
            }}
          >
            <span className="mr-2">{service.icon}</span>
            {service.name}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HeroSection;
