// Background service worker for YouTube Summary extension
'use strict';

interface InfoResponse {
  success: boolean;
  videoId?: string;
  title?: string;
  error?: string;
  cookies?: chrome.cookies.Cookie[];
}

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCookies') {
    handleGetCookies().then(sendResponse);
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'getVideoInfo') {
    handleGetVideoInfo(sender.tab).then(sendResponse);
    return true;
  }
  return false;
});

async function handleGetCookies(): Promise<InfoResponse> {
  try {
    const cookies = await chrome.cookies.getAll({ domain: '.youtube.com' });
    return { success: true, cookies };
  } catch (error) {
    return { success: false, error: (error as Error).message };
  }
}

async function handleGetVideoInfo(tab?: chrome.tabs.Tab): Promise<InfoResponse> {
  if (!tab?.url) {
    return { success: false, error: 'No tab URL' };
  }

  try {
    const url = new URL(tab.url);
    const videoId = url.searchParams.get('v');
    
    if (!videoId) {
      return { success: false, error: 'Not a video page' };
    }

    return {
      success: true,
      videoId,
      title: tab.title?.replace(' - YouTube', '').trim() || 'Unknown',
    };
  } catch (error) {
    return { success: false, error: (error as Error).message };
  }
}

// Context menu for right-click summarization
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'summarize-video',
    title: 'Summarize this video',
    contexts: ['page', 'link'],
    documentUrlPatterns: ['https://www.youtube.com/*', 'https://youtube.com/*'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'summarize-video') {
    console.log('Context menu clicked for video summarization');
  }
});
