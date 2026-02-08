// State
export {};

let currentVideoId: string | null = null;
let currentCookies: string | null = null;

interface Elements {
  statusContainer: HTMLElement;
  status: HTMLElement;
  notYoutube: HTMLElement;
  videoInfo: HTMLElement;
  videoThumbnail: HTMLImageElement;
  videoTitle: HTMLElement;
  videoId: HTMLElement;
  cookieIndicator: HTMLElement;
  cookieText: HTMLElement;
  summarizeBtn: HTMLButtonElement;
  btnText: HTMLElement;
  btnLoading: HTMLElement;
  resultContainer: HTMLElement;
  result: HTMLElement;
  copyBtn: HTMLButtonElement;
  newSummaryBtn: HTMLButtonElement;
  serverUrlInput: HTMLInputElement;
}

// DOM Elements
const elements = {
  statusContainer: document.getElementById('status-container')!,
  status: document.getElementById('status')!,
  notYoutube: document.getElementById('not-youtube')!,
  videoInfo: document.getElementById('video-info')!,
  videoThumbnail: document.getElementById('video-thumbnail') as HTMLImageElement,
  videoTitle: document.getElementById('video-title')!,
  videoId: document.getElementById('video-id')!,
  cookieIndicator: document.getElementById('cookie-indicator')!,
  cookieText: document.getElementById('cookie-text')!,
  // summarizeBtn, btnText, etc. are now top-level consts
  resultContainer: document.getElementById('result-container')!,
  result: document.getElementById('result')!,
  copyBtn: document.getElementById('copy-btn') as HTMLButtonElement,
  newSummaryBtn: document.getElementById('new-summary-btn') as HTMLButtonElement,
  serverUrlInput: document.getElementById('server-url') as HTMLInputElement,
};

const summarizeBtn = document.getElementById('summarize-btn') as HTMLButtonElement;
const btnText = summarizeBtn.querySelector('.btn-text') as HTMLSpanElement;
const btnLoading = summarizeBtn.querySelector('.btn-loading') as HTMLSpanElement;
const sendCookiesCheckbox = document.getElementById('send-cookies') as HTMLInputElement;


// Types for API
interface ApiSummaryBody {
  id?: string;
  format: string;
  cookies?: string;
  transcript?: string;
  title?: string;
  userAgent?: string;
}

// Global YouTube Response Type
declare global {
  interface Window {
    ytInitialPlayerResponse?: {
      captions?: {
        playerCaptions?: Array<{
          captionTrack?: Array<{
            languageCode: string;
            kind?: string;
            baseUrl: string;
          }>;
        }>;
        playerCaptionsTracklistRenderer?: {
          captionTracks?: Array<{
            baseUrl: string;
            name?: { simpleText: string };
            vssId?: string;
            languageCode: string;
            kind?: string;
          }>;
        };
      };
    };
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', init);

// Constants
// Constants
const DEFAULT_API_URL = 'https://pyytsum.ddoffy.org';


async function init() {
  // Button handlers
  summarizeBtn.addEventListener('click', summarizeVideo as EventListener);
  elements.copyBtn.addEventListener('click', copyResult as EventListener);
  elements.newSummaryBtn.addEventListener('click', resetUI as EventListener);
  elements.serverUrlInput.addEventListener('change', saveServerUrl);

  // Load settings
  await loadSettings();

  // Check current tab
  await checkCurrentTab();
}


async function checkCurrentTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab?.url) {
      showNotYoutube();
      return;
    }

    const url = new URL(tab.url);
    
    // Check if it's a YouTube video page
    if (!url.hostname.includes('youtube.com')) {
      showNotYoutube();
      return;
    }

    // Extract video ID
    const videoId = url.searchParams.get('v');
    if (!videoId) {
      showNotYoutube();
      return;
    }

    currentVideoId = videoId;
    
    // Show video info
    elements.notYoutube.classList.add('hidden');
    elements.videoInfo.classList.remove('hidden');
    
    // Set thumbnail
    elements.videoThumbnail.src = `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`;
    elements.videoId.textContent = `ID: ${videoId}`;

    // Get video title from tab
    if (tab.title) {
      elements.videoTitle.textContent = tab.title.replace(' - YouTube', '').trim();
    }

    // Fetch cookies
    await fetchCookies();

  } catch (error) {
    console.error('Error checking tab:', error);
    showStatus('Error checking current tab', 'error');
  }
}

function showNotYoutube() {
  elements.notYoutube.classList.remove('hidden');
  elements.videoInfo.classList.add('hidden');
}

async function fetchCookies() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.url || !tab.id) return;

    // Use current tab's store ID (handles incognito/containers)
    const storeId = await getCurrentCookieStoreId(tab.id);
    
    // Fetch all cookies for the current URL
    const details = { url: tab.url, storeId };
    
    let cookies = await chrome.cookies.getAll(details);
    
    if (cookies.length === 0) {
      elements.cookieIndicator.className = 'indicator warning';
      elements.cookieText.textContent = 'Not logged in';
      currentCookies = null;
      return;
    }

    // Convert to Netscape cookie format for yt-dlp
    currentCookies = formatCookiesForYtDlp(cookies);
    
    // Check for auth cookies
    const hasAuth = cookies.some(c => 
      c.name === 'SAPISID' || 
      c.name === 'SID' || 
      c.name === '__Secure-1PSID'
    );

    if (hasAuth) {
      elements.cookieIndicator.className = 'indicator success';
      elements.cookieText.textContent = 'Logged in';
    } else {
      elements.cookieIndicator.className = 'indicator warning';
      elements.cookieText.textContent = 'Not logged in';
    }

  } catch (error) {
    console.error('Error fetching cookies:', error);
    elements.cookieIndicator.className = 'indicator error';
    elements.cookieText.textContent = 'Cookie error';
    currentCookies = null;
  }
}

async function getCurrentCookieStoreId(tabId: number): Promise<string> {
  const stores = await chrome.cookies.getAllCookieStores();
  const store = stores.find((s) => s.tabIds.includes(tabId));
  return store ? store.id : '0';
}

function formatCookiesForYtDlp(cookies: chrome.cookies.Cookie[]): string {
  let output = '# Netscape HTTP Cookie File\n';
  output += '# https://curl.haxx.se/rfc/cookie_spec.html\n';
  output += '# This is a generated file! Do not edit.\n\n';

  for (const cookie of cookies) {
    const domain = cookie.domain;
    const includeSubdomains = domain.startsWith('.') ? 'TRUE' : 'FALSE';
    const path = cookie.path;
    const secure = cookie.secure ? 'TRUE' : 'FALSE';
    const expiry = cookie.expirationDate ? Math.floor(cookie.expirationDate).toString() : '0';
    
    // Sanitize cookie value
    const safeValue = cookie.value.replace(/[\t\n\r]/g, '');
    
    output += `${domain}\t${includeSubdomains}\t${path}\t${secure}\t${expiry}\t${cookie.name}\t${safeValue}\n`;
  }

  return output;
}

async function getTranscriptFromPage(): Promise<string | null> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return null;

  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: 'MAIN',
    func: () => {
      // Logic to execute in the page context (must be self-contained or use stringified args)
      try {
        // 1. Check for player response object
        const playerResponse = (window as any).ytInitialPlayerResponse;
        if (!playerResponse) {
            console.log('YTSum: No ytInitialPlayerResponse found');
            return null;
        }

        // 2. Extract caption tracks
        // Check both playerCaptions and playerCaptionsTracklistRenderer
        let tracks = playerResponse.captions?.playerCaptions?.[0]?.captionTrack;
        if (!tracks || !tracks.length) {
            tracks = playerResponse.captions?.playerCaptionsTracklistRenderer?.captionTracks;
        }
        
        if (!tracks || !tracks.length) {
            console.log('YTSum: No caption tracks found in player response');
            return null;
        }

        // 3. Find English track (or auto-generated English)
        // Helper to find best track
        const findBestTrack = (tracks: any[]) => {
            // Priority: .vssId matching .en > .kind = 'asr' & .languageCode = 'en' > first 'en'
            let t = tracks.find((ot: any) => ot.vssId === '.en');
            if (!t) {
                t = tracks.find((ot: any) => ot.languageCode === 'en' && ot.kind === 'asr');
            }
            if (!t) {
                t = tracks.find((ot: any) => ot.languageCode === 'en');
            }
            // Fallback to first available if no English track is found
            if (!t && tracks.length > 0) {
                t = tracks[0];
            }
            return t;
        };

        const track = findBestTrack(tracks);
        
        if (!track) {
            console.log('YTSum: No suitable caption track found (empty list or no English/fallback)');
            return null;
        }

        console.log('YTSum: Found caption track:', track.name?.simpleText || track.languageCode, track.baseUrl);

        // 4. Fetch the transcript XML/JSON from the baseUrl
        let url = track.baseUrl;
        url = /[?&]fmt=/.test(url)
          ? url.replace(/([?&]fmt=)[^&]*/, '$1vtt')
          : url + (url.includes('?') ? '&' : '?') + 'fmt=vtt';

        return fetch(url)
          .then(resp => {
            if (!resp.ok) {
              console.warn(`YTSum: Failed to fetch transcript from ${url}, status: ${resp.status}`);
              return null;
            }
            return resp.text();
          })
          .then(vtt => {
            if (!vtt) return null;

            const segments: string[] = [];
            for (const raw of vtt.split('\n')) {
              const line = raw.trim();
              if (!line || line.startsWith('WEBVTT') || line.startsWith('Kind:') ||
                  line.startsWith('Language:') || line.includes('-->')) continue;
              const cleaned = line.replace(/<[^>]+>/g, '').trim();
              if (!cleaned) continue;
              if (segments.length && segments[segments.length - 1] === cleaned) continue;
              segments.push(cleaned);
            }
            console.log(`YTSum: Extracted ${segments.length} segments from page.`);
            return segments.join(' ') || null;
          })
          .catch(e => {
            console.warn('YTSum: Error fetching or parsing VTT:', e);
            return null;
          });
                 
      } catch (e) {
        console.warn('YTSum: Error extracting transcript in page context:', e);
        return null;
      }
    }
  });

  if (!results || !results[0] || !results[0].result) {
    console.log('YTSum: No transcript result from executeScript.');
    return null;
  }
  return results[0].result;
}

async function summarizeVideo() {
  if (!currentVideoId) {
    showStatus('No video selected', 'error');
    return;
  }

  setLoading(true);
  hideStatus();
  elements.resultContainer.classList.add('hidden');

  try {
    const requestBody: ApiSummaryBody = {
      id: currentVideoId,
      format: 'json',
    };

    try {
      const transcript = await getTranscriptFromPage();
      if (transcript) {
        requestBody.transcript = transcript;
        if (elements.videoTitle.textContent) {
            requestBody.title = elements.videoTitle.textContent;
        }
        console.log(`Transcript extracted from page (${transcript.length} chars)`);
      }
    } catch (e) {
      console.warn('Client-side transcript extraction failed:', e);
    }

    if (currentCookies) {
      requestBody.cookies = currentCookies;
      requestBody.userAgent = navigator.userAgent;
    }

    const apiUrl = elements.serverUrlInput.value.replace(/\/$/, '');
    console.log('Sending request to:', `${apiUrl}/api/summary`);

    const response = await fetch(`${apiUrl}/api/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(errorText || `HTTP ${response.status}`);
    }

    const data = await response.json();
    if (data.results && data.results.length > 0) {
      const first = data.results[0];
      if (first.error) {
        throw new Error(first.error);
      }
      elements.result.textContent = first.summary || 'No summary available';
    } else {
      throw new Error('No results returned');
    }

    elements.resultContainer.classList.remove('hidden');
    showStatus('Summary generated successfully!', 'success');

  } catch (error) {
    console.error('Error summarizing:', error);
    showStatus(`Error: ${((error as Error).message)}`, 'error');
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading: boolean) {
  if (isLoading) {
    summarizeBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoading.classList.remove('hidden');
    elements.resultContainer.classList.add('hidden');
  } else {
    summarizeBtn.disabled = false;
    btnText.classList.remove('hidden');
    btnLoading.classList.add('hidden');
  }
}

function showStatus(message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') {
  elements.status.textContent = message;
  elements.status.className = `status ${type}`;
  elements.statusContainer.classList.remove('hidden');
}

function hideStatus() {
  elements.statusContainer.classList.add('hidden');
}

async function copyResult() {
  try {
    await navigator.clipboard.writeText(elements.result.textContent || '');
    const originalText = elements.copyBtn.textContent;
    elements.copyBtn.textContent = 'Copied!';
    setTimeout(() => {
      elements.copyBtn.textContent = originalText;
    }, 2000);
  } catch (error) {
    console.error('Failed to copy:', error);
    showStatus('Failed to copy to clipboard', 'error');
  }
}

function resetUI() {
  elements.resultContainer.classList.add('hidden');
  hideStatus();
}

async function loadSettings() {
  try {
    const result = await chrome.storage.local.get(['serverUrl']);
    if (result.serverUrl) {
      elements.serverUrlInput.value = result.serverUrl;
    } else {
      elements.serverUrlInput.value = DEFAULT_API_URL;
    }
  } catch (error) {
    console.error('Error loading settings:', error);
    elements.serverUrlInput.value = DEFAULT_API_URL;
  }
}

async function saveServerUrl() {
  try {
    let url = elements.serverUrlInput.value.trim();
    if (!url) {
      url = DEFAULT_API_URL;
      elements.serverUrlInput.value = url;
    }
    await chrome.storage.local.set({ serverUrl: url });
  } catch (error) {
    console.error('Error saving settings:', error);
  }
}
