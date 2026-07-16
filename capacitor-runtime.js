// capacitor-runtime.js

// Mock mode for testing in browser without native plugins
if (location.search.includes('mock=true')) {
  window.Capacitor = {
    isMock: true,
    Plugins: {
      Network: {
        getStatus: () => Promise.resolve({ connected: false }),
        addListener: (name, cb) => {
          window._networkCallback = cb;
          console.log('[Network Mock] Listener added');
        }
      },
      Haptics: {
        impact: (opts) => {
          console.log('%c[Haptics Impact Mock] ' + opts.style, 'color: #9B6BFF; font-weight: bold;');
          return Promise.resolve();
        }
      },
      SplashScreen: {
        hide: () => {
          console.log('[SplashScreen Mock] hide() called');
          return Promise.resolve();
        }
      }
    }
  };

  // Add floating helper button to toggle online mode
  window.addEventListener('DOMContentLoaded', () => {
    const btn = document.createElement('button');
    btn.id = 'mock-toggle-online';
    btn.innerText = 'Mock: Go Online';
    btn.style.cssText = 'position:fixed; bottom:16px; right:16px; z-index:100000; padding:10px 16px; background:#33D6A6; color:#06070B; font-weight:bold; border:none; border-radius:10px; cursor:pointer; font-family:sans-serif; box-shadow: 0 4px 12px rgba(51,214,166,0.3);';
    btn.onclick = () => {
      if (btn.innerText === 'Mock: Go Online') {
        if (window._networkCallback) window._networkCallback({ connected: true });
        btn.innerText = 'Mock: Go Offline';
        btn.style.background = '#FF6B6B';
        btn.style.color = '#fff';
      } else {
        if (window._networkCallback) window._networkCallback({ connected: false });
        btn.innerText = 'Mock: Go Online';
        btn.style.background = '#33D6A6';
        btn.style.color = '#06070B';
      }
    };
    document.body.appendChild(btn);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('Capacitor runtime initialized.');

  // 1. Initialize Haptics Click Listener
  initHaptics();

  // 2. Initialize Network Monitoring
  initNetwork();

  // 3. Hide Splash Screen after a short delay to ensure rendering is complete
  initSplashScreen();
});

function initHaptics() {
  const triggerHaptic = async () => {
    try {
      const Haptics = window.Capacitor?.Plugins?.Haptics;
      if (Haptics) {
        await Haptics.impact({ style: 'LIGHT' });
      }
    } catch (err) {
      console.warn('Haptics error:', err);
    }
  };

  // Add click listener to document
  document.addEventListener('click', (e) => {
    const interactive = e.target.closest('button, a, input[type="submit"], input[type="button"], [role="button"], .rf-btn, .rf-glass, .tab-btn, .topic-card, .vocab-card');
    if (interactive) {
      triggerHaptic();
    }
  });
}

function initNetwork() {
  const Network = window.Capacitor?.Plugins?.Network;
  if (!Network) return;

  // Create and append the offline overlay element
  const overlay = document.createElement('div');
  overlay.id = 'native-offline-overlay';
  overlay.innerHTML = `
    <div class="offline-content">
      <div class="offline-icon-glow">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#9B6BFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="offline-icon">
          <path d="M1 1l22 22M16.72 11.06A10.94 10.94 0 0 1 19 12.5a12.94 12.94 0 0 1 2.63 2.69M5.58 5.58A10.84 10.84 0 0 0 1 11.58a12.94 12.94 0 0 0 4.13 6.84M8.9 8.9a6.83 6.83 0 0 0-3.9 2.68 8.65 8.65 0 0 0 2.27 4.73M12 11.58v.01M17.42 17.42a6.84 6.84 0 0 1-5.42 1.16M14 14.24a3.17 3.17 0 0 0-2 .34"></path>
        </svg>
      </div>
      <h2>Connection Lost</h2>
      <p>Please check your internet connection. We will automatically reconnect you once you're back online.</p>
      <button class="rf-btn" id="offline-retry-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        Try Reconnecting
      </button>
    </div>
  `;

  // Append overlay style
  const style = document.createElement('style');
  style.textContent = `
    #native-offline-overlay {
      position: fixed;
      inset: 0;
      background: #06070B;
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      color: #EDEEF3;
      font-family: 'Inter', sans-serif;
      transition: opacity 0.4s ease, visibility 0.4s ease;
      opacity: 0;
      visibility: hidden;
    }
    #native-offline-overlay.active {
      opacity: 1;
      visibility: visible;
    }
    #native-offline-overlay .offline-content {
      text-align: center;
      max-width: 360px;
      animation: rf-fadein 0.4s ease both;
    }
    #native-offline-overlay .offline-icon-glow {
      position: relative;
      width: 100px;
      height: 100px;
      margin: 0 auto 24px;
      background: rgba(155, 107, 255, 0.08);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #native-offline-overlay .offline-icon {
      animation: pulse 2s infinite ease-in-out;
    }
    #native-offline-overlay h2 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 12px;
      background: linear-gradient(90deg, #6EA8FE, #B78CFF);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
    #native-offline-overlay p {
      font-size: 14px;
      line-height: 1.6;
      opacity: 0.65;
      margin-bottom: 28px;
    }
    #native-offline-overlay .rf-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #5B8DEF, #9B6BFF);
      border: none;
      color: white;
      padding: 12px 24px;
      border-radius: 14px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      box-shadow: 0 8px 24px rgba(155, 107, 255, 0.25);
      transition: all 0.2s;
    }
    #native-offline-overlay .rf-btn:active {
      transform: scale(0.97);
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.08); opacity: 0.7; }
    }
  `;
  document.head.appendChild(style);
  document.body.appendChild(overlay);

  const updateStatus = (connected) => {
    if (connected) {
      overlay.classList.remove('active');
    } else {
      overlay.classList.add('active');
    }
  };

  // Check initial state
  Network.getStatus().then(status => {
    updateStatus(status.connected);
  });

  // Listen for network changes
  Network.addListener('networkStatusChange', status => {
    updateStatus(status.connected);
  });

  // Retry button
  document.getElementById('offline-retry-btn').addEventListener('click', async () => {
    const status = await Network.getStatus();
    updateStatus(status.connected);
  });
}

function initSplashScreen() {
  const SplashScreen = window.Capacitor?.Plugins?.SplashScreen;
  if (SplashScreen) {
    // Hide splash screen after a short delay (e.g. 600ms) to let the page render
    setTimeout(() => {
      SplashScreen.hide().catch(err => console.warn('SplashScreen error:', err));
    }, 600);
  }
}

// Native-compatible file download handler using Filesystem and Share plugins
window.downloadTextFile = async (filename, textContent) => {
  const Filesystem = window.Capacitor?.Plugins?.Filesystem;
  const Share = window.Capacitor?.Plugins?.Share;
  
  if (!window.Capacitor || !Filesystem || !Share) {
    // Fallback for standard browsers
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const dlLink = document.createElement('a');
    dlLink.href = url;
    dlLink.download = filename;
    dlLink.click();
    URL.revokeObjectURL(url);
    return;
  }

  try {
    // Write temporary text file to the CACHE directory
    const result = await Filesystem.writeFile({
      path: filename,
      data: textContent,
      directory: 'CACHE',
      encoding: 'utf8'
    });

    // Share the file path via native Share sheet (allows saving to Files or sending via apps)
    await Share.share({
      title: filename,
      text: 'ReadForge AI practice text.',
      url: result.uri
    });
  } catch (err) {
    console.error('Failed to share/download file:', err);
  }
};
