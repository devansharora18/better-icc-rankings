import React from "react";
import Navbar from "../components/Navbar"
import { iplRatings } from "./ipl_ratings";


export default function Page() {

	return (
		<div className="bg-white font-sans">
      <Navbar />
	  

      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
          aria-hidden="true"
        >
          <div
            className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          />
        </div>
        <div className="mx-auto max-w-2xl py-4 sm:py-6 lg:py-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              IPL Rankings
            </h1>  
          </div>
		  <div>
		  <div className="-m-1.5 overflow-x-auto pt-5">
            <div className="p-1.5 min-w-full inline-block align-middle">
              <div className="overflow-hidden">
			<table className="min-w-full divide-y divide-black">
                  <thead>
                    <tr>
                      <th scope="col" className="px-6 py-3 text-start text-xs font-medium uppercase">
                        Ranking
                      </th>
                      <th scope="col" className="px-6 py-3 text-start text-xs font-medium uppercase">
                        Team
                      </th>
                      <th scope="col" className="px-6 py-3 text-start text-xs font-medium uppercase">
                        Elo
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-black dark:divide-black">
                    {iplRatings.map((team, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">
                          {index + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{team.team}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{team.elo.toFixed(0)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
				</div>
				</div>
				</div>
		  </div>
        </div>
        <div
          className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
          aria-hidden="true"
        >
          <div
            className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          />
        </div>
      </div>
    </div>
	);
}
