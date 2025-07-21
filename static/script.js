// Import the PDF.js library as a module
import * as pdfjsLib from 'https://mozilla.github.io/pdf.js/build/pdf.mjs';

// Configure the PDF.js worker using the imported library
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://mozilla.github.io/pdf.js/build/pdf.worker.mjs`;

// Your application code follows...
const fileInput = document.getElementById('resume_file');
const textarea = document.getElementById('resume_text');
const form = document.getElementById('resumeForm');
const submitButton = document.getElementById('submitButton');
const resultBox = document.getElementById('resultBox');
const resultContent = document.getElementById('resultContent');

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0];
  if (!file) return;

  if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const typedArray = new Uint8Array(e.target.result);
        const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise;
        let fullText = '';
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const textContent = await page.getTextContent();
          fullText += textContent.items.map(item => item.str).join(' ') + '\n';
        }
        textarea.value = fullText.trim() || '(No text found in PDF)';
      } catch (err) {
        console.error("PDF extraction error:", err);
        textarea.value = '(Could not extract text from PDF)';
      }
    };
    reader.readAsArrayBuffer(file);
  } else if (
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    file.name.endsWith('.docx')
  ) {
    const reader = new FileReader();
    reader.onload = (e) => {
      mammoth.extractRawText({ arrayBuffer: e.target.result })
        .then(result => { textarea.value = result.value.trim() || '(No text found in DOCX)'; })
        .catch((err) => {
          console.error("DOCX extraction error:", err);
          textarea.value = '(Could not extract text from DOCX)';
        });
    };
    reader.readAsArrayBuffer(file);
  } else {
    alert('Unsupported file type. Please upload PDF or DOCX.');
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const textToFix = textarea.value.trim();
  if (!textToFix) {
    alert('Please either paste your resume or upload a file.');
    return;
  }
  submitButton.disabled = true;
  submitButton.textContent = 'Fixing...';
  resultBox.style.display = 'none';
  resultContent.textContent = '';

  try {
    const resp = await fetch('/api/fix-resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: textToFix }),
    });

    const data = await resp.json();

    if (!resp.ok) {
        throw new Error(data.error || 'An unknown server error occurred.');
    }

    resultContent.textContent = data.fixed_resume;
    resultBox.style.display = 'block';

  } catch (err) {
    resultContent.textContent = 'Error: ' + err.message;
    resultBox.style.display = 'block';
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Fix My Resume';
  }
});