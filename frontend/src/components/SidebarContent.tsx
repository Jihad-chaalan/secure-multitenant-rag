// src/components/SidebarContent.tsx

import { Fragment } from "react";
import { Link, useLocation } from "react-router-dom";
import { Listbox, Transition } from "@headlessui/react";
import { useAppStore } from "../store/useAppStore";
import { DEPARTMENTS, ROLES_MAP } from "../utils/constants";

// ✅ Inline SVG Icons (no external dependency)
const ChevronUpDownIcon = () => (
  <svg className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4 text-blue-600 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

export default function SidebarContent() {
  const { department, role, setDepartment, setRole } = useAppStore();
  const location = useLocation();

  const driveFolderLink =
    "https://drive.google.com/drive/folders/1nKe_ZsnnfX92fV0ue6IhCeqLW75-AzNt";

  const isChatActive = location.pathname === "/";
  const isAdminActive = location.pathname === "/admin";

  const handleDepartmentChange = (newDept: string) => {
    setDepartment(newDept);
    setRole(ROLES_MAP[newDept][0]);
  };

  return (
    <>
      {/* Header */}
      <div className="px-6 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            R
          </div>
          <div>
            <h1 className="text-sm font-semibold text-gray-800 dark:text-gray-100 tracking-tight">
              Secure RAG
            </h1>
            <p className="text-[10px] text-gray-400 dark:text-gray-500 font-medium uppercase tracking-wider">
              Multi-Tenant · Enterprise
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links — ONLY visible on mobile */}
      <div className="lg:hidden px-6 py-3 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700/50 rounded-lg p-0.5">
          <Link
            to="/"
            className={`
              flex-1 px-3 py-1.5 rounded-md text-sm font-medium text-center transition-all duration-200
              ${
                isChatActive
                  ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              }
            `}
          >
            💬 Chat
          </Link>
          <Link
            to="/admin"
            className={`
              flex-1 px-3 py-1.5 rounded-md text-sm font-medium text-center transition-all duration-200
              ${
                isAdminActive
                  ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              }
            `}
          >
            📊 Dashboard
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-6 py-5 space-y-6 overflow-y-auto">
        {/* Context Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Context
            </span>
            <span className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          <div className="space-y-3.5">
            {/* Department - Custom Dropdown */}
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">
                Department
              </label>
              <Listbox value={department} onChange={handleDepartmentChange}>
                <div className="relative">
                  <Listbox.Button
                    className={`
                      w-full text-sm border border-gray-200 dark:border-gray-700 
                      rounded-lg px-3.5 py-2.5 
                      bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 
                      focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 
                      outline-none transition cursor-pointer text-left
                      flex items-center justify-between
                    `}
                  >
                    <span className="truncate">{department.replace("_", " ")}</span>
                    <ChevronUpDownIcon />
                  </Listbox.Button>
                  <Transition
                    as={Fragment}
                    leave="transition ease-in duration-100"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                  >
                    <Listbox.Options
                      className={`
                        absolute z-10 mt-1 w-full 
                        bg-white dark:bg-gray-800 
                        border border-gray-200 dark:border-gray-700 
                        rounded-lg shadow-lg 
                        max-h-48 overflow-auto
                        text-sm
                      `}
                    >
                      {DEPARTMENTS.map((dept) => (
                        <Listbox.Option
                          key={dept}
                          value={dept}
                          className={({ active }) =>
                            `
                            relative cursor-pointer select-none py-2 px-3
                            ${active ? "bg-blue-50 dark:bg-blue-900/30" : ""}
                            ${dept === department ? "font-medium" : ""}
                          `
                          }
                        >
                          {({ selected }) => (
                            <div className="flex items-center justify-between">
                              <span className="truncate">{dept.replace("_", " ")}</span>
                              {selected && <CheckIcon />}
                            </div>
                          )}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </Listbox>
            </div>

            {/* Role - Custom Dropdown */}
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">
                Role
              </label>
              <Listbox value={role} onChange={setRole}>
                <div className="relative">
                  <Listbox.Button
                    className={`
                      w-full text-sm border border-gray-200 dark:border-gray-700 
                      rounded-lg px-3.5 py-2.5 
                      bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 
                      focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 
                      outline-none transition cursor-pointer text-left
                      flex items-center justify-between
                    `}
                  >
                    <span className="truncate">{role}</span>
                    <ChevronUpDownIcon />
                  </Listbox.Button>
                  <Transition
                    as={Fragment}
                    leave="transition ease-in duration-100"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                  >
                    <Listbox.Options
                      className={`
                        absolute z-10 mt-1 w-full 
                        bg-white dark:bg-gray-800 
                        border border-gray-200 dark:border-gray-700 
                        rounded-lg shadow-lg 
                        max-h-48 overflow-auto
                        text-sm
                      `}
                    >
                      {ROLES_MAP[department].map((r) => (
                        <Listbox.Option
                          key={r}
                          value={r}
                          className={({ active }) =>
                            `
                            relative cursor-pointer select-none py-2 px-3
                            ${active ? "bg-blue-50 dark:bg-blue-900/30" : ""}
                            ${r === role ? "font-medium" : ""}
                          `
                          }
                        >
                          {({ selected }) => (
                            <div className="flex items-center justify-between">
                              <span className="truncate">{r}</span>
                              {selected && <CheckIcon />}
                            </div>
                          )}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </Listbox>
            </div>
          </div>
        </div>

        {/* Active Context Badge */}
        <div className="bg-blue-50 dark:bg-blue-950/30 rounded-xl border border-blue-100 dark:border-blue-800/50 p-3.5">
          <p className="text-[10px] font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            Active Context
          </p>
          <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 mt-0.5">
            {department} / {role}
          </p>
        </div>

        {/* Data Source Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Data Source
            </span>
            <span className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 p-3.5 space-y-2">
            <a
              href={driveFolderLink}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm5-1c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm5-1c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" />
              </svg>
              📁 View Documents
            </a>
            <p className="text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
              This folder contains all documents ingested by the RAG system.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
              System Online
            </span>
          </div>
          <span className="text-[10px] text-gray-400 dark:text-gray-500 font-mono">
            v2.0
          </span>
        </div>
      </div>
    </>
  );
}