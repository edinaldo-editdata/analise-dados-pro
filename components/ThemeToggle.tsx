import React, { useEffect, useState } from 'react';

export const ThemeToggle: React.FC = () => {
  const [isDark, setIsDark] = useState<boolean>(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initialDark = stored ? stored === 'dark' : prefersDark;
      setIsDark(initialDark);
      document.documentElement.classList.toggle('dark', initialDark);
    } catch (e) {
      console.error('Theme init error', e);
    }
  }, []);

  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  };

  return (
    <button
      onClick={toggleTheme}
      className="inline-flex items-center gap-2 rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      aria-label="Alternar tema"
      title={isDark ? 'Tema escuro' : 'Tema claro'}
    >
      <span className="relative inline-block w-5 h-5">
        {isDark ? (
          // Moon
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M21.752 15.002A9.718 9.718 0 0 1 12.06 22C6.5 22 2 17.5 2 12c0-4.252 2.664-7.88 6.4-9.3a.75.75 0 0 1 .931.986A9 9 0 0 0 20.25 15a.75.75 0 0 1 1.502.002Z" />
          </svg>
        ) : (
          // Sun
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm0 4a1 1 0 0 1-1-1v-1a1 1 0 1 1 2 0v1a1 1 0 0 1-1 1Zm0-20a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0V3a1 1 0 0 1 1-1Zm10 10a1 1 0 0 1-1 1h-1a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1ZM3 12a1 1 0 0 1-1-1H1a1 1 0 1 1 0 2h1a1 1 0 0 1 1-1Zm15.657 6.657a1 1 0 0 1-1.414 0l-.707-.707a1 1 0 1 1 1.414-1.414l.707.707a1 1 0 0 1 0 1.414ZM6.464 6.464A1 1 0 1 1 5.05 5.05l.707-.707a1 1 0 1 1 1.414 1.414l-.707.707Zm12.728-8.485a1 1 0 0 1 0 1.414l-.707.707A1 1 0 1 1 17.071 0l.707-.707a1 1 0 0 1 1.414 0ZM6.464 17.536a1 1 0 0 1 0 1.414l-.707.707A1 1 0 1 1 4.343 18.243l.707-.707a1 1 0 0 1 1.414 0Z" />
          </svg>
        )}
      </span>
      <span>{isDark ? 'Escuro' : 'Claro'}</span>
    </button>
  );
};