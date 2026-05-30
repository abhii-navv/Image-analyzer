const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewWrap = document.getElementById('preview-wrap');
const previewImg = document.getElementById('preview-img');
const previewName = document.getElementById('preview-name');
const analyzeBtn = document.getElementById('analyze-btn');
const changeBtn = document.getElementById('change-btn');
const form = document.getElementById('upload-form');

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewName.textContent = file.name;
    dropZone.style.display = 'none';
    previewWrap.style.display = 'block';
    analyzeBtn.disabled = false;
  };
  reader.readAsDataURL(file);
}

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('active');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('active'));

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('active');
  const file = e.dataTransfer.files[0];
  if (file) showPreview(file);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showPreview(fileInput.files[0]);
});

changeBtn.addEventListener('click', () => {
  previewWrap.style.display = 'none';
  dropZone.style.display = 'block';
  analyzeBtn.disabled = true;
  fileInput.value = '';
});

form.addEventListener('submit', () => {
  analyzeBtn.disabled = true;

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    inset: 0;
    background: #0D1410;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  `;

  overlay.innerHTML = `
    <div style="text-align:center; max-width:360px; padding:2rem; width:100%;">
      <div id="loading-icon" style="
        font-size: 2.5rem;
        color: #5CBA8A;
        margin-bottom: 1.5rem;
        display: block;
        animation: pulse 1.5s ease-in-out infinite;
      ">&#9670;</div>

      <h2 style="
        color: #E8F0EB;
        font-size: 1.4rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
      ">Analyzing your photo</h2>

      <p style="
        color: #7A9485;
        font-size: 0.9rem;
        margin-bottom: 2rem;
      ">Gemini AI is studying your image...</p>

      <div style="
        width: 100%;
        height: 4px;
        background: #1A2420;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 1.2rem;
      ">
        <div id="loading-bar" style="
          height: 100%;
          width: 0%;
          background: #5CBA8A;
          border-radius: 2px;
          transition: width 0.5s ease;
        "></div>
      </div>

      <p id="loading-step" style="
        color: #7A9485;
        font-size: 0.82rem;
      ">Reading brightness & focus...</p>
    </div>

    <style>
      @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.85); }
      }
    </style>
  `;

  document.body.appendChild(overlay);

  const steps = [
    { text: "Reading brightness & focus...", progress: 10 },
    { text: "Sending image to Gemini AI...", progress: 25 },
    { text: "Analyzing colors and details...", progress: 40 },
    { text: "Generating Lightroom settings...", progress: 55 },
    { text: "Generating Snapseed settings...", progress: 70 },
    { text: "Writing beginner tips...", progress: 85 },
    { text: "Almost ready...", progress: 95 }
  ];

  let i = 0;
  const bar = document.getElementById('loading-bar');
  const stepText = document.getElementById('loading-step');

  const interval = setInterval(() => {
    if (i < steps.length) {
      stepText.textContent = steps[i].text;
      bar.style.width = steps[i].progress + '%';
      i++;
    } else {
      clearInterval(interval);
    }
  }, 2000);
});