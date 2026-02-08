// Content script for YouTube pages
// This script runs on YouTube pages and can interact with the page content

interface VideoInfo {
  videoId: string;
  title: string;
  url: string;
}

(function() {
  'use strict';

  // Expose video info to the extension
  function getVideoInfo(): VideoInfo | null {
    const videoId = new URLSearchParams(window.location.search).get('v');
    if (!videoId) return null;

    // Try to get title from page
    let title = document.title.replace(' - YouTube', '').trim();
    
    // Try to get from meta tag
    const metaTitle = document.querySelector('meta[name="title"]');
    if (metaTitle && (metaTitle as HTMLMetaElement).content) {
      title = (metaTitle as HTMLMetaElement).content;
    }

    // Try to get from video player
    const playerTitle = document.querySelector('#above-the-fold #title h1 yt-formatted-string');
    if (playerTitle && playerTitle.textContent) {
      title = playerTitle.textContent.trim();
    }

    return {
      videoId,
      title,
      url: window.location.href,
    };
  }

  // Listen for messages from popup/background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getVideoInfo') {
      const info = getVideoInfo();
      sendResponse(info);
      return true;
    }
    return false;
  });

  console.log('[YouTube Summary] Content script loaded');
})();
