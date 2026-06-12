/**
 * Main application entry point.
 * Keep modules in js/ and import or load them from here as the site grows.
 */

const handleDOMReady = () => {
  document.documentElement.classList.add('js');
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', handleDOMReady);
} else {
  handleDOMReady();
}
