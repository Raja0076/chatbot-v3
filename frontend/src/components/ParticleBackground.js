import React from "react";
import Particles from "react-tsparticles";

function ParticleBackground() {
  return (
    <Particles
      options={{
        fullScreen: { enable: true, zIndex: -1 },

        background: {
          color: "#020617",
        },

        particles: {
          number: {
            value: 120,
            density: {
              enable: true,
              area: 800,
            },
          },

          color: {
            value: ["#38bdf8", "#60a5fa", "#22d3ee"],
          },

          links: {
            enable: true,
            distance: 140,
            color: "#38bdf8",
            opacity: 0.35,
            width: 1,
          },

          move: {
            enable: true,
            speed: 1.2,
            direction: "none",
            outModes: {
              default: "bounce",
            },
          },

          size: {
            value: { min: 1, max: 3 },
          },

          opacity: {
            value: 0.6,
          },
        },

        interactivity: {
          events: {
            onHover: {
              enable: true,
              mode: "grab",
            },
            onClick: {
              enable: true,
              mode: "push",
            },
          },

          modes: {
            grab: {
              distance: 180,
              links: {
                opacity: 0.6,
              },
            },

            push: {
              quantity: 4,
            },
          },
        },

        detectRetina: true,
      }}
    />
  );
}

export default ParticleBackground;