import { NavLink } from "react-router-dom"
import { useState } from "react"
import { 
  Home, 
  ImagePlus, 
  FileCheck2,
  ScanSearch,
  LayoutDashboard, 
  History, 
  Leaf,
  Info,
  Sun,
  Moon,
  Menu,
  X
} from "lucide-react"

interface SidebarProps {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export default function Sidebar({ theme, toggleTheme }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false)

  const navItems = [
    { name: "Home", path: "/", icon: Home },
    { name: "Analyze", path: "/analyze", icon: ImagePlus },
    { name: "Results", path: "/results", icon: FileCheck2 },
    { name: "Explainability", path: "/explainability", icon: ScanSearch },
    { name: "Research Dashboard", path: "/research", icon: LayoutDashboard },
    { name: "History", path: "/history", icon: History },
    { name: "Plant Care Guide", path: "/plant-care", icon: Leaf },
    { name: "About", path: "/about", icon: Info },
  ]

  const closeSidebar = () => setIsOpen(false)

  return (
    <>
      <button 
        className="lg:hidden fixed top-4 right-4 z-50 p-2 bg-card rounded-md shadow-md dark:bg-[#252b32] dark:text-gray-100"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      <aside className={`fixed left-0 top-0 bottom-0 w-64 bg-white dark:bg-[#1f2429] border-r border-gray-200 dark:border-gray-800 p-6 flex flex-col z-40 transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="flex items-center gap-3 mb-10 text-emerald-500">
          <Leaf className="w-8 h-8" />
          <div>
            <h1 className="font-bold text-xl tracking-tight text-gray-900 dark:text-gray-100">PlantIntel <span className="text-emerald-500 font-light">AI</span></h1>
            <p className="text-[10px] uppercase tracking-wider text-gray-500 dark:text-gray-400">Detect • Explain • Quantify</p>
          </div>
        </div>

        <nav className="flex-1 space-y-2 overflow-y-auto pr-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={closeSidebar}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                    isActive
                      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm">{item.name}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-800">
          <button 
            onClick={toggleTheme}
            className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-300"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            <span className="text-sm">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
        </div>
      </aside>
      
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden" 
          onClick={closeSidebar}
        />
      )}
    </>
  )
}
