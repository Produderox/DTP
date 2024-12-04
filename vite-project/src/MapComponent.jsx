import React, { useEffect, useState } from "react";
import { csv } from "d3-fetch";
import { scaleLinear } from "d3-scale";
import { Tooltip as ReactTooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import {
  ComposableMap,
  Geographies,
  Geography,
  Sphere,
  Graticule
} from "react-simple-maps";

const geoUrl = "/features.json";


const colorScale = scaleLinear()
  .domain([0, 100])
  .range(["#ffedea", "#ff5233"]);

const MapComponent = () => {
  const [data, setData] = useState([]);

  const [content, setContent] = useState("");

  useEffect(() => {
    csv(`/Mapdata.csv`).then((data) => {
      setData(data);
    });
  }, []);

  return (
    <>
    <ReactTooltip id="country" float>{content}</ReactTooltip>
    <ComposableMap data-tooltip-id="country"
    data-tooltip-content=""
      projectionConfig={{
        rotate: [-10, 0, 0],
        scale: 147
      }}
    >
      {data.length > 0 && (
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const d = data.find((s) => s['Country Name'] === geo.properties.name);
              return (
                <Geography
                  key={geo.rsmkey}
                  geography={geo}
                  data-tooltip-id="country"
                  fill={d ? colorScale(d["2021"]) : "#F5F4F6"}
                  onMouseEnter={() => {
                    setContent(`${geo.properties.name} | ${Math.round(d["2021"])}%`);
                    console.log(content)
                  }}
                  onMouseLeave={() => {
                    setContent("");
                  }}
                  style={{
                    hover: {
                      fill: "#F53",
                      outline: "none"
                    },
                    pressed: {
                      fill: "#E42",
                      outline: "none"
                    }
                  }}
                />
              );
            })
          }
        </Geographies>
      )}
    </ComposableMap>
    </>
  );
};

export default MapComponent;
