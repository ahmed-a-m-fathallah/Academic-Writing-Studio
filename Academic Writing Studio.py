"""
Academic Writing Studio
A local Python + HTML/JS application tailored for Urban Planning and Academic Writing.

Prerequisites:
pip install flask requests beautifulsoup4 nltk PyPDF2 scikit-learn numpy
"""

import os
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

# --- INITIALIZATION & NLP SETUP ---
print("Downloading required NLTK NLP data...")
nltk_packages = ['wordnet', 'punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng', 'omw-1.4']
for pkg in nltk_packages:
    try:
        nltk.data.find(f'corpora/{pkg}')
    except LookupError:
        try:
            nltk.data.find(f'tokenizers/{pkg}')
        except LookupError:
            try:
                nltk.data.find(f'taggers/{pkg}')
            except LookupError:
                nltk.download(pkg, quiet=True)

lemmatizer = WordNetLemmatizer()
app = Flask(__name__)

# --- HTML/CSS/JS FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Writing Studio</title>
    <!-- Professional Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts for Fallback if Century Gothic isn't local -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- Vis.js for Mindmap -->
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        /* --- CSS VARIABLES & THEMES --- */
        :root {
            --primary-color: #2c3e50;
            --primary: #3498db; /* Mapped accent/primary */
            --primary-hover: #2980b9;
            --bg-color: #f8f9fa;
            --panel-bg: #ffffff;
            --border-color: #e0e0e0;
            --text-color: #333333;
            --toolbar-bg: #f1f3f4;
            --font-main: "Century Gothic", "Tw Cen MT", "Montserrat", sans-serif;
            --danger: #dc2626;
            --success: #16a34a;
        }

        [data-theme="dark"] {
            --bg-color: #0f172a;
            --panel-bg: #1e293b;
            --toolbar-bg: #0f172a; 
            --text-color: #f8fafc;
            --border-color: #334155;
            --primary-color: #f8fafc;
            --primary: #38bdf8;
            --primary-hover: #7dd3fc;
        }

        * { box-sizing: border-box; font-family: var(--font-main); }
        
        body {
            margin: 0; padding: 0; background-color: var(--bg-color); color: var(--text-color);
            display: flex; flex-direction: column; height: 100vh; overflow: hidden;
            transition: background-color 0.3s ease;
        }

        /* --- HEADER --- */
        header {
            background-color: var(--panel-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 60px;
            z-index: 100;
        }

        .brand {
            font-weight: 600;
            font-size: 1.2em;
            color: var(--primary);
            display: flex;
            flex-direction: column;
            line-height: 1.2;
        }
        .brand span { font-size: 0.70em; color: #666; font-weight: 400; opacity: 0.8; }
        [data-theme="dark"] .brand span { color: #cbd5e1; }

        .header-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        button, .btn-label, select, input[type="text"], input[type="number"], input[type="color"] {
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: var(--panel-bg);
            color: var(--text-color);
            padding: 6px 12px;
            border-radius: 4px;
            font-family: var(--font-main);
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            outline: none;
        }
        input[type="text"], input[type="number"] { cursor: text; }
        button:hover, .btn-label:hover { background-color: rgba(0,0,0,0.05); }
        button.primary { background-color: var(--primary); color: white; border: none; font-weight: 600; }
        button.primary:hover { background-color: var(--primary-hover); }

        /* --- MAIN LAYOUT --- */
        .workspace { display: flex; flex: 1; overflow: hidden; background-color: var(--toolbar-bg); }
        
        .panel {
            display: flex; flex-direction: column;
            background: var(--panel-bg);
            overflow: hidden;
        }

        #toc-panel { width: 250px; flex-shrink: 0; border-right: 1px solid var(--border-color); }
        #editor-panel { flex: 1; background-color: #e9ecef; display: flex; flex-direction: column; }
        [data-theme="dark"] #editor-panel { background-color: #0f172a; }
        #research-panel { width: 350px; flex-shrink: 0; border-left: 1px solid var(--border-color); }

        /* --- RESIZERS --- */
        .resizer {
            width: 8px; cursor: col-resize; background-color: transparent;
            position: relative; z-index: 10; flex-shrink: 0;
            display: flex; justify-content: center; align-items: center;
        }
        .resizer::after {
            content: ''; display: block; width: 2px; height: 30px; background-color: var(--border-color);
            border-radius: 2px; transition: background-color 0.2s;
        }
        .resizer:hover::after, .resizer.active::after { background-color: var(--primary); }

        /* --- TOC STYLES --- */
        .toc-header { padding: 15px; font-weight: 600; background: rgba(0,0,0,0.02); border-bottom: 1px solid var(--border-color); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
        .toc-content { padding: 15px 10px; overflow-y: auto; flex: 1; font-size: 13.5px; }
        .toc-item { cursor: pointer; color: var(--text-color); margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transition: color 0.2s; padding: 4px; border-bottom: 1px dashed var(--border-color); }
        .toc-item:hover { color: var(--primary); }
        .toc-h1 { font-weight: bold; margin-left: 0; border-bottom: none; }
        .toc-h2 { margin-left: 15px; color: #666; font-size: 0.95em; }
        [data-theme="dark"] .toc-h2 { color: #cbd5e1; }

        /* --- EDITOR STYLES --- */
        .toolbar {
            padding: 8px 15px; border-bottom: 1px solid var(--border-color); background: var(--panel-bg);
            display: flex; gap: 8px; flex-wrap: wrap; align-items: center; font-size: 13px; z-index: 5;
        }
        
        .toolbar-group { display: flex; gap: 4px; border-right: 1px solid var(--border-color); padding-right: 12px; align-items: center; }
        .toolbar-group:last-child { border-right: none; }
        
        .toolbar-btn {
            width: 32px; height: 32px; padding: 0; display: flex; justify-content: center; align-items: center;
            border: 1px solid transparent; background: transparent; border-radius: 4px; color: var(--text-color);
        }
        .toolbar-btn:hover { background-color: rgba(0,0,0,0.05); border-color: var(--border-color); }
        .toolbar-btn i { font-size: 14px; }
        
        /* Word-like Canvas (Fixed Clipping & Top Margin) */
        .canvas-container {
            flex: 1; 
            overflow-y: auto; 
            padding: 40px 20px; 
            display: block; 
        }
        
        #editor {
            margin: 0 auto; 
            width: 210mm; 
            min-height: 297mm; 
            background-color: var(--panel-bg);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
            padding: 25mm 30mm; 
            outline: none; 
            color: var(--text-color); 
            font-size: 11pt; 
            
            --editor-line-height: 1.5;
            line-height: var(--editor-line-height);
            transition: padding 0.3s ease;
        }

        #editor p, #editor h1, #editor h2, #editor h3, #editor div, #editor ul, #editor ol {
            line-height: inherit;
        }
        
        #editor > *:first-child { 
            margin-top: 0 !important; 
        }
        
        #editor h1 { font-size: 18pt; color: var(--primary); margin-top: 24pt; margin-bottom: 6pt; }
        #editor h2 { font-size: 14pt; margin-top: 18pt; margin-bottom: 6pt; color: var(--primary-color); }
        #editor p { margin-top: 0; margin-bottom: 12pt; text-align: justify; }
        #editor blockquote { border-left: 4px solid var(--primary); margin-left: 0; padding-left: 20px; font-style: italic; opacity: 0.8; }
        
        .editor-status {
            display: flex; justify-content: flex-end; gap: 15px; padding: 6px 12px;
            background: var(--panel-bg); border-top: 1px solid var(--border-color);
            font-size: 12px; color: var(--text-color); opacity: 0.8; font-weight: bold;
            z-index: 5;
        }

        /* --- RESEARCH PANE --- */
        .tabs { display: flex; background: rgba(0,0,0,0.02); border-bottom: 1px solid var(--border-color); flex-shrink: 0;}
        .tab {
            flex: 1; padding: 12px; text-align: center; cursor: pointer; font-size: 13.5px;
            border-bottom: 2px solid transparent; font-weight: 500; color: var(--text-color);
            transition: all 0.2s;
        }
        .tab.active { background: var(--panel-bg); font-weight: bold; border-bottom-color: var(--primary); color: var(--primary); }
        .tab-content { flex: 1; display: none; flex-direction: column; overflow: hidden; height: 100%; }
        .tab-content.active { display: flex; }

        /* Crawler UI */
        .search-bar { padding: 15px; display: flex; gap: 8px; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; flex-shrink: 0; }
        .search-bar input[type="text"] { flex: 1; min-width: 150px; }
        .results-table { flex: 1; overflow-y: auto; padding: 0; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 12px 15px; border-bottom: 1px solid var(--border-color); font-size: 13px; }
        th { background: rgba(0,0,0,0.02); position: sticky; top: 0; font-weight: 600;}
        a { color: var(--primary); text-decoration: none; font-weight: bold;}
        a:hover { text-decoration: underline; }
        .cite-btn { font-size: 11px; padding: 4px 8px; margin-top: 4px; display: inline-block; }

        /* PDF Viewer */
        #pdf-controls { padding: 10px 15px; border-bottom: 1px solid var(--border-color); display: flex; gap: 10px; align-items: center; flex-shrink: 0; }
        #pdf-frame { flex: 1 1 auto; width: 100%; height: 100%; border: none; min-height: 0; display: block; }
        .pdf-notes { height: 80px; min-height: 40px; resize: vertical; border-top: 1px solid var(--border-color); padding: 10px 15px; background: var(--panel-bg); outline: none; overflow-y: auto; flex-shrink: 0; }

        /* Mindmap UI */
        #mindmap-canvas { flex: 1 1 auto; width: 100%; height: 100%; background: var(--panel-bg); min-height: 0; }
        .mindmap-tools { padding: 10px 15px; border-bottom: 1px solid var(--border-color); display: flex; gap: 8px; align-items: center; flex-wrap: wrap; flex-shrink: 0; }

        /* Dialogs */
        #synonym-popup {
            position: absolute; display: none; background: var(--panel-bg);
            border: 1px solid var(--border-color); box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            padding: 10px; border-radius: 6px; z-index: 1000; width: 280px;
        }
        .synonym-chip {
            display: inline-block; padding: 6px 10px; margin: 3px;
            background: var(--bg-color); border-radius: 4px; cursor: pointer; font-size: 13px;
            border: 1px solid var(--border-color); transition: 0.2s;
        }
        .synonym-chip:hover { background: var(--primary); color: white; border-color: var(--primary); }
        
        /* Focus Mode & Pomodoro */
        .pomodoro-container {
            display: inline-flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.04);
            padding: 4px 12px; border-radius: 4px; border: 1px solid var(--border-color); font-family: monospace; font-size: 14px;
        }
        .pomodoro-container button { border: none; background: transparent; cursor: pointer; color: var(--primary); font-size: 12px; padding: 0 4px; }
        .pomodoro-container button:hover { background: transparent; opacity: 0.7; }
        
        body.focus-mode #toc-panel, body.focus-mode #research-panel, body.focus-mode .resizer { display: none !important; }
        body.focus-mode .canvas-container { padding: 40px 20px; }
        
    </style>
</head>
<body data-theme="light">

    <header>
        <div class="brand">
            Academic Writing Studio
            <span>Urban Planning & AI Integrated Research Environment</span>
        </div>
        <div class="header-controls">
            <div class="pomodoro-container" title="Pomodoro Writing Sprint Timer">
                🍅 <span id="pomo-timer">25:00</span>
                <button onclick="togglePomodoro()" id="pomo-btn"><i class="fa-solid fa-play"></i></button>
                <button onclick="resetPomodoro()" style="color:var(--danger)"><i class="fa-solid fa-rotate-right"></i></button>
            </div>
            <button onclick="document.body.classList.toggle('focus-mode')" title="Hide side panels for creative flow"><i class="fa-solid fa-expand"></i> Focus Mode</button>
            <select id="theme-selector" onchange="changeTheme()">
                <option value="light">Light Mode</option>
                <option value="dark">Dark Mode</option>
            </select>
            <button onclick="exportSession()"><i class="fa-solid fa-floppy-disk"></i> Save (.aws)</button>
            <label for="import-file" class="btn-label"><i class="fa-solid fa-folder-open"></i> Load (.aws)</label>
            <input type="file" id="import-file" accept=".aws,.json" style="display:none;" onchange="importSession(event)">
        </div>
    </header>

    <div class="workspace">
        
        <!-- TABLE OF CONTENTS PANE -->
        <div class="panel" id="toc-panel">
            <div class="toc-header">Table of Contents</div>
            <div class="toc-content" id="toc-content">
                <span style="opacity:0.5;">Add H1/H2 headings in the editor to populate...</span>
            </div>
        </div>

        <div class="resizer" id="resizer-1"></div>

        <!-- WRITING PANE -->
        <div class="panel" id="editor-panel">
            <div class="toolbar">
                <div class="toolbar-group">
                    <select id="phrasebank" onchange="insertPhrase()" style="max-width: 200px;">
                        <option value="">+ Insert Academic Phrase</option>
                        <optgroup label="1. Topic: Urban Contexts">
                            <option value="Cities are complex systems that encompass ">Cities are complex systems that encompass...</option>
                            <option value="The physical environment plays a crucial role in shaping ">The physical environment plays a crucial role in shaping...</option>
                            <option value="Urban vitality serves as a key indicator of ">Urban vitality serves as a key indicator of...</option>
                        </optgroup>
                        <optgroup label="2. Methodological Approaches">
                            <option value="This study introduces a hybrid spatial learning method integrating ">This study introduces a hybrid spatial learning method...</option>
                            <option value="GIS offers a robust mechanism to analyse... ">GIS offers a robust mechanism to analyse...</option>
                        </optgroup>
                        <optgroup label="3. Identifying Gaps & Limitations">
                            <option value="However, little attention has been paid to the socio-spatial variables in ">However, little attention has been paid to the socio-spatial variables in...</option>
                            <option value="The current shift highlights a gap in ">The current shift highlights a gap in...</option>
                        </optgroup>
                    </select>
                </div>
                
                <div class="toolbar-group">
                    <select id="formatSelector" onchange="formatDoc('formatBlock', this.value); this.selectedIndex=0;" title="Text Format / Heading">
                        <option value="" disabled selected>Style</option>
                        <option value="P">Paragraph (Normal)</option>
                        <option value="H1">Heading 1</option>
                        <option value="H2">Heading 2</option>
                    </select>
                    <!-- ADDED FONT FAMILY SELECTOR -->
                    <select id="fontFamily" onchange="formatDoc('fontName', this.value)" title="Font Type">
                        <option value="" disabled selected>Font</option>
                        <option value="Century Gothic">Century Gothic</option>
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Arial">Arial</option>
                        <option value="Georgia">Georgia</option>
                    </select>
                    <select id="fontSize" onchange="formatDoc('fontSize', this.value)">
                        <option value="3">Font Size</option>
                        <option value="1">Small</option>
                        <option value="4">Large</option>
                        <option value="5">X-Large</option>
                    </select>
                    <input type="color" id="textColor" title="Text Color" onchange="formatDoc('foreColor', this.value)" value="#1e293b" style="padding:0; width: 32px; height: 32px; border:none; background:transparent;">
                </div>
                
                <div class="toolbar-group">
                    <button class="toolbar-btn" onclick="formatDoc('bold')" title="Bold"><i class="fa-solid fa-bold"></i></button>
                    <button class="toolbar-btn" onclick="formatDoc('italic')" title="Italic"><i class="fa-solid fa-italic"></i></button>
                    <button class="toolbar-btn" onclick="formatDoc('underline')" title="Underline"><i class="fa-solid fa-underline"></i></button>
                </div>
                
                <div class="toolbar-group">
                    <button class="toolbar-btn" onclick="formatDoc('justifyLeft')" title="Align Left"><i class="fa-solid fa-align-left"></i></button>
                    <button class="toolbar-btn" onclick="formatDoc('justifyCenter')" title="Align Center"><i class="fa-solid fa-align-center"></i></button>
                    <button class="toolbar-btn" onclick="formatDoc('justifyRight')" title="Align Right"><i class="fa-solid fa-align-right"></i></button>
                    <button class="toolbar-btn" onclick="formatDoc('justifyFull')" title="Justify"><i class="fa-solid fa-align-justify"></i></button>
                </div>

                <div class="toolbar-group">
                    <select id="pageMargins" onchange="changePageMargins(this.value)" title="Page Margins">
                        <option value="" disabled selected>◱ Margins</option>
                        <option value="normal">Normal</option>
                        <option value="narrow">Narrow</option>
                        <option value="wide">Wide</option>
                    </select>
                    <select id="lineSpacing" onchange="changeLineSpacing(this.value)" title="Line/Vertical Spacing">
                        <option value="" disabled selected>↕ Spacing</option>
                        <option value="1.0">1.0 (Single)</option>
                        <option value="1.15">1.15</option>
                        <option value="1.5">1.5</option>
                        <option value="2.0">2.0 (Double)</option>
                    </select>
                </div>

                <div class="toolbar-group" style="margin-left: auto; border:none; padding-right:0;">
                    <button class="primary" onclick="checkGrammarLocal()"><i class="fa-solid fa-spell-check"></i> Tone & Grammar</button>
                    <button onclick="triggerSynonymButton()" title="Select a word in the editor first"><i class="fa-solid fa-magnifying-glass"></i> Synonyms</button>
                </div>
            </div>
            
            <div class="canvas-container">
                <div id="editor" class="editor-canvas" contenteditable="true" spellcheck="false" placeholder="Draft your urban planning manuscript here. Use the 'Style' dropdown to add structural Headings..."></div>
            </div>
            
            <div class="editor-status">
                <span id="word-count">0 Words</span>
                <span id="char-count">0 Characters</span>
                <span id="read-time">0 min read</span>
            </div>
        </div>

        <div class="resizer" id="resizer-2"></div>

        <!-- RESEARCH & PDF PANE -->
        <div class="panel" id="research-panel">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('crawler')">Literature Crawler</div>
                <div class="tab" onclick="switchTab('pdf')">PDF Viewer</div>
                <div class="tab" onclick="switchTab('mindmap')">Mindmap Graph</div>
            </div>

            <!-- Web Crawler Content -->
            <div id="crawler-content" class="tab-content active">
                <div class="search-bar">
                    <input type="text" id="search-query" placeholder="Topic (e.g. Graph Neural Networks)">
                    <select id="search-source">
                        <option value="openalex">OpenAlex</option>
                        <option value="semantic">Semantic Scholar</option>
                        <option value="arxiv">arXiv API</option>
                        <option value="crossref">Crossref</option>
                        <option value="google">Google Scholar</option>
                    </select>
                    <input type="number" id="result-count" value="10" min="1" max="100" style="width: 70px;">
                    <button class="primary" onclick="runCrawler()"><i class="fa-solid fa-search"></i> Search</button>
                </div>
                <div class="results-table">
                    <table id="results-table">
                        <thead>
                            <tr>
                                <th>Author / Year</th>
                                <th>Title</th>
                                <th>Link</th>
                            </tr>
                        </thead>
                        <tbody id="results-body">
                            <tr><td colspan="3" style="text-align:center;">Enter a topic to search official academic APIs.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- PDF Viewer Content -->
            <div id="pdf-content" class="tab-content">
                <div id="pdf-controls">
                    <button class="primary" onclick="document.getElementById('pdf-upload').click()"><i class="fa-solid fa-cloud-arrow-up"></i> Select PDF</button>
                    <input type="file" id="pdf-upload" accept="application/pdf" onchange="loadLocalPDF()" style="display:none;">
                    <span style="font-size: 11px; opacity: 0.8; margin-left: 8px;">Use native highlights.</span>
                </div>
                <iframe id="pdf-frame" src=""></iframe>
                <div contenteditable="true" class="pdf-notes" placeholder="PDF notes (Saved with session)"></div>
            </div>

            <!-- Mindmap Graph Content -->
            <div id="mindmap-content" class="tab-content">
                <div class="mindmap-tools">
                    <input type="file" id="auto-mindmap-pdfs" accept=".pdf" multiple="multiple" style="display:none;" onchange="autoAnalyzePDFs(event)">
                    <button class="primary" onclick="document.getElementById('auto-mindmap-pdfs').click()" style="background-color: var(--success);"><i class="fa-solid fa-wand-magic-sparkles"></i> Upload & Analyze Multiple PDFs</button>
                    <span style="border-left:1px solid #ccc; height:20px; margin: 0 5px;"></span>
                    <button onclick="addMindmapEdge()"><i class="fa-solid fa-link"></i> Link</button>
                    <button onclick="deleteSelectedMindmap()"><i class="fa-solid fa-trash"></i></button>
                </div>
                <div id="mindmap-status" style="font-size:12px; font-style:italic; padding: 10px 15px; flex-shrink: 0; background: rgba(0,0,0,0.02); border-bottom: 1px solid var(--border-color);">Click the button above and select multiple PDFs (Hold Ctrl/Cmd) to generate the graph.</div>
                <div id="mindmap-canvas"></div>
            </div>
        </div>
    </div>

    <!-- Popup for Synonyms -->
    <div id="synonym-popup"></div>

    <script>
        // --- GLOBAL STATE ---
        let network = null;
        let nodes = new vis.DataSet([]);
        let edges = new vis.DataSet([]);
        let currentSearchResults = []; 
        let currentSearchQuery = "";
        let currentSearchSource = "openalex";
        let currentSearchCount = 10;
        let pomoInterval = null;
        let pomoTime = 25 * 60;
        let pomoRunning = false;

        // --- INITIALIZATION ---
        document.addEventListener('DOMContentLoaded', () => {
            initResizers();
            document.getElementById('editor').addEventListener('input', () => {
                updateTOC();
                updateLiveMetrics();
            });
            updateTOC();
            updateLiveMetrics();
        });
        
        // --- CREATIVE/PROFESSIONAL ADDONS ---
        function updateLiveMetrics() {
            const text = document.getElementById('editor').innerText.trim();
            const words = text ? text.split(/\s+/).length : 0;
            const chars = text.length;
            const readTime = Math.ceil(words / 200); // Avg 200 wpm
            
            document.getElementById('word-count').innerText = `${words} Words`;
            document.getElementById('char-count').innerText = `${chars} Characters`;
            document.getElementById('read-time').innerText = `${readTime} min read`;
        }

        function formatTime(seconds) {
            const m = Math.floor(seconds / 60).toString().padStart(2, '0');
            const s = (seconds % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function togglePomodoro() {
            const btn = document.getElementById('pomo-btn');
            if (pomoRunning) {
                clearInterval(pomoInterval);
                pomoRunning = false;
                btn.innerHTML = '<i class="fa-solid fa-play"></i>';
            } else {
                pomoRunning = true;
                btn.innerHTML = '<i class="fa-solid fa-pause"></i>';
                pomoInterval = setInterval(() => {
                    if (pomoTime > 0) {
                        pomoTime--;
                        document.getElementById('pomo-timer').innerText = formatTime(pomoTime);
                    } else {
                        clearInterval(pomoInterval);
                        pomoRunning = false;
                        btn.innerHTML = '<i class="fa-solid fa-play"></i>';
                        alert("Pomodoro session complete! Take a creative break.");
                    }
                }, 1000);
            }
        }

        function resetPomodoro() {
            clearInterval(pomoInterval);
            pomoRunning = false;
            pomoTime = 25 * 60;
            document.getElementById('pomo-timer').innerText = formatTime(pomoTime);
            document.getElementById('pomo-btn').innerHTML = '<i class="fa-solid fa-play"></i>';
        }
        
        function copyCitation(authors, year, title, link) {
            const citation = `${authors} (${year}). ${title}. Retrieved from ${link}`;
            navigator.clipboard.writeText(citation).then(() => {
                alert("APA Citation copied to clipboard!");
            }).catch(err => {
                const textArea = document.createElement("textarea");
                textArea.value = citation;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand("copy");
                document.body.removeChild(textArea);
                alert("APA Citation copied to clipboard!");
            });
        }

        // --- RESIZERS ---
        function initResizers() {
            let isResizing = false;
            let currentResizer = null;

            document.querySelectorAll('.resizer').forEach(resizer => {
                resizer.addEventListener('mousedown', function(e) {
                    isResizing = true;
                    currentResizer = resizer;
                    document.body.style.cursor = 'col-resize';
                    resizer.classList.add('active');
                    e.preventDefault(); 
                });
            });

            document.addEventListener('mousemove', function(e) {
                if (!isResizing) return;
                const workspace = document.querySelector('.workspace');
                const workspaceRect = workspace.getBoundingClientRect();
                
                if (currentResizer.id === 'resizer-1') {
                    let newWidth = e.clientX - workspaceRect.left;
                    if (newWidth > 100 && newWidth < 400) document.getElementById('toc-panel').style.width = newWidth + 'px';
                } else if (currentResizer.id === 'resizer-2') {
                    let newWidth = workspaceRect.right - e.clientX;
                    if (newWidth > 250 && newWidth < workspaceRect.width * 0.7) document.getElementById('research-panel').style.width = newWidth + 'px';
                }
            });

            document.addEventListener('mouseup', function(e) {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.cursor = 'default';
                    currentResizer.classList.remove('active');
                    currentResizer = null;
                    if (network && document.getElementById('mindmap-content').classList.contains('active')) network.redraw();
                }
            });
        }

        // --- DYNAMIC TABLE OF CONTENTS ---
        function updateTOC() {
            const editor = document.getElementById('editor');
            const tocContent = document.getElementById('toc-content');
            const headings = editor.querySelectorAll('h1, h2');
            
            tocContent.innerHTML = '';
            if (headings.length === 0) {
                tocContent.innerHTML = '<span style="opacity:0.5;">Add H1/H2 headings in the editor to populate...</span>';
                return;
            }

            headings.forEach((heading, index) => {
                if (!heading.id) heading.id = 'heading-id-' + index;
                const div = document.createElement('div');
                div.className = `toc-item ${heading.tagName.toLowerCase() === 'h1' ? 'toc-h1' : 'toc-h2'}`;
                div.innerText = heading.innerText || 'Untitled Section';
                div.title = heading.innerText;
                
                div.onclick = () => {
                    heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    const originalColor = heading.style.color;
                    heading.style.color = 'var(--danger)';
                    setTimeout(() => { heading.style.color = originalColor; }, 800);
                };
                tocContent.appendChild(div);
            });
        }

        // --- THEMES ---
        function changeTheme() {
            document.body.setAttribute('data-theme', document.getElementById('theme-selector').value);
        }

        // --- TABS ---
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if(tab === 'crawler') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('crawler-content').classList.add('active');
            } else if (tab === 'pdf') {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('pdf-content').classList.add('active');
            } else {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('mindmap-content').classList.add('active');
                if(!network) initMindmap();
                else setTimeout(() => { network.redraw(); network.fit(); }, 50);
            }
        }

        // --- EDITOR FORMATTING ---
        function formatDoc(cmd, value=null) {
            document.execCommand(cmd, false, value);
            document.getElementById('editor').focus();
            updateTOC(); 
        }

        function insertPhrase() {
            const select = document.getElementById('phrasebank');
            if (select.value) {
                document.execCommand('insertText', false, select.value);
                select.value = ""; 
                document.getElementById('editor').focus();
            }
        }

        function changeLineSpacing(val) {
            document.getElementById('editor').style.setProperty('--editor-line-height', val);
        }
        
        function changePageMargins(val) {
            const editor = document.getElementById('editor');
            if (val === 'narrow') {
                editor.style.padding = '12mm 15mm';
            } else if (val === 'wide') {
                editor.style.padding = '35mm 40mm';
            } else {
                editor.style.padding = '25mm 30mm';
            }
        }

        // --- LOCAL GRAMMAR CHECKER ---
        async function checkGrammarLocal() {
            const editor = document.getElementById('editor');
            const text = editor.innerText;
            if(!text.trim()) return;

            try {
                const response = await fetch('/api/grammar_local', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text: text })
                });
                const issues = await response.json();
                
                if (issues.length === 0) {
                    alert("No structural grammar issues found.");
                } else {
                    let msg = `Found ${issues.length} potential issues to review:\n\n`;
                    issues.forEach((iss, idx) => {
                        msg += `${idx+1}. [${iss.type}] "${iss.match}" -> ${iss.suggestion}\n`;
                    });
                    alert(msg);
                }
            } catch (err) {
                alert("Grammar check failed.");
            }
        }

        // --- SYNONYMS (FIXED CUTOFF) ---
        let currentSelectionRange = null;

        function triggerSynonymButton() {
            const selection = window.getSelection();
            if (selection.rangeCount > 0 && selection.toString().trim().length > 0) {
                currentSelectionRange = selection.getRangeAt(0).cloneRange();
                const word = selection.toString().trim();
                const rect = currentSelectionRange.getBoundingClientRect();
                fetchSynonyms(word, rect);
            } else {
                alert("Please highlight a single word in the editor first.");
            }
        }

        async function fetchSynonyms(word, rect) {
            if (word.split(/\s+/).length > 2) return; 

            const popup = document.getElementById('synonym-popup');
            
            // Setup loading state to get initial height calculations
            popup.innerHTML = "<em>Finding synonyms...</em>";
            popup.style.display = 'block';
            
            const updatePopupPosition = () => {
                const popupHeight = popup.offsetHeight;
                const spaceBelow = window.innerHeight - rect.bottom;
                
                if (spaceBelow < popupHeight + 10) {
                    // Render above the word
                    popup.style.top = `${rect.top + window.scrollY - popupHeight - 5}px`;
                } else {
                    // Render below the word
                    popup.style.top = `${rect.bottom + window.scrollY + 5}px`;
                }
                popup.style.left = `${Math.max(10, rect.left + window.scrollX)}px`;
            };
            
            updatePopupPosition();

            try {
                const response = await fetch(`/api/synonyms?word=${encodeURIComponent(word)}`);
                const data = await response.json();
                
                if (data.synonyms.length === 0) {
                    popup.innerHTML = "<small>No synonyms found.</small>";
                } else {
                    popup.innerHTML = `<div style="font-weight:bold;margin-bottom:5px;font-size:14px;border-bottom:1px solid var(--border-color);padding-bottom:4px;">Synonyms for '${word}'</div>`;
                    data.synonyms.forEach(syn => {
                        const span = document.createElement('span');
                        span.className = 'synonym-chip';
                        span.innerText = syn;
                        span.onclick = () => {
                            const sel = window.getSelection();
                            sel.removeAllRanges();
                            sel.addRange(currentSelectionRange);
                            document.execCommand('insertText', false, syn);
                            popup.style.display = 'none';
                            document.getElementById('editor').focus();
                        };
                        popup.appendChild(span);
                    });
                }
                updatePopupPosition(); // Readjust after inserting contents
            } catch(e) {
                popup.innerHTML = "<small>Error loading synonyms.</small>";
                updatePopupPosition();
            }
            
            document.addEventListener('click', function hidePopup(e) {
                if (!popup.contains(e.target) && e.target.id !== 'editor' && !e.target.closest('.toolbar-btn')) {
                    popup.style.display = 'none';
                    document.removeEventListener('click', hidePopup);
                }
            });
        }

        // --- WEB CRAWLER ---
        async function runCrawler() {
            currentSearchQuery = document.getElementById('search-query').value;
            currentSearchSource = document.getElementById('search-source').value;
            currentSearchCount = document.getElementById('result-count').value;
            
            if(!currentSearchQuery) return;

            const tbody = document.getElementById('results-body');
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;">Querying official API... Please wait.</td></tr>`;

            try {
                const response = await fetch(`/api/search`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: currentSearchQuery, source: currentSearchSource, count: currentSearchCount })
                });
                const results = await response.json();
                currentSearchResults = results; 
                renderSearchResults();
            } catch(e) {
                tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:red;">Error fetching API data. Target server may be down.</td></tr>`;
            }
        }

        function renderSearchResults() {
            const tbody = document.getElementById('results-body');
            tbody.innerHTML = '';
            if(!currentSearchResults || currentSearchResults.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No results found.</td></tr>`;
                return;
            }
            currentSearchResults.forEach(res => {
                const tr = document.createElement('tr');
                const safeTitle = res.title.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const safeAuthors = res.authors.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                tr.innerHTML = `
                    <td>${res.authors}<br><small>(${res.year})</small></td>
                    <td style="font-weight:bold; color:var(--primary);">${res.title}</td>
                    <td>
                        <a href="${res.link}" target="_blank">Link</a>
                        <button class="cite-btn" onclick="copyCitation('${safeAuthors}', '${res.year}', '${safeTitle}', '${res.link}')"><i class="fa-solid fa-quote-right"></i> Cite (APA)</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // --- PDF VIEWER ---
        function loadLocalPDF() {
            const file = document.getElementById('pdf-upload').files[0];
            if (file) {
                const fileURL = URL.createObjectURL(file);
                document.getElementById('pdf-frame').src = fileURL;
            }
        }

        // --- MINDMAP GRAPH (Vis.js) ---
        function initMindmap() {
            const container = document.getElementById('mindmap-canvas');
            const data = { nodes: nodes, edges: edges };
            const options = {
                interaction: { hover: true, multiselect: true, tooltipDelay: 200 },
                manipulation: { enabled: false },
                physics: { stabilization: true, barnesHut: { springLength: 200, centralGravity: 0.1 } },
                nodes: { font: { face: 'Century Gothic', color: '#1e293b' }, borderWidth: 2 },
                edges: { arrows: 'to', font: {face: 'Century Gothic', size: 11, align: 'middle'}, smooth: {type: 'continuous'} }
            };
            network = new vis.Network(container, data, options);
        }

        async function autoAnalyzePDFs(event) {
            const files = event.target.files;
            if(!files || files.length === 0) return;

            const status = document.getElementById('mindmap-status');
            status.innerText = "Extracting Academic Noun Phrases and analyzing semantic overlap... Please wait.";
            
            const formData = new FormData();
            for(let i=0; i<files.length; i++) {
                formData.append('pdfs', files[i]);
            }

            try {
                const response = await fetch('/api/analyze_pdfs', { method: 'POST', body: formData });
                
                if (!response.ok) {
                   let errorMsg = `Server Error (${response.status}).`;
                   try {
                       const errData = await response.json();
                       if (errData.error) errorMsg = `Analysis failed: ${errData.error}`;
                   } catch(e) {
                       // Handled HTML page fallback errors
                   }
                   status.innerText = errorMsg;
                   return;
                }
                
                const data = await response.json();
                if(data.error) {
                    status.innerText = "Analysis failed.";
                    return;
                }

                nodes.clear();
                edges.clear();
                nodes.add(data.nodes);
                edges.add(data.edges);
                
                if(!network) initMindmap();
                switchTab('mindmap');
                
                setTimeout(() => { network.redraw(); network.fit(); }, 100);
                status.innerText = `Successfully mapped precise NLP insights from ${files.length} documents.`;
            } catch (err) {
                status.innerText = "Network error during analysis.";
            }
        }

        function addMindmapEdge() {
            const selected = network.getSelectedNodes();
            if (selected.length === 2) {
                const relation = prompt("Relationship (e.g., Conflicts, Supports):", "Shared Focus");
                edges.add({ from: selected[0], to: selected[1], label: relation || '', color: '#94a3b8' });
            } else {
                alert("Please select exactly two nodes (Hold Ctrl + Click) to link them.");
            }
        }

        function deleteSelectedMindmap() {
            const selection = network.getSelection();
            nodes.remove(selection.nodes);
            edges.remove(selection.edges);
        }

        // --- EXPORT/IMPORT ---
        function exportSession() {
            const sessionData = {
                editor: document.getElementById('editor').innerHTML,
                pdfNotes: document.querySelector('.pdf-notes').innerHTML,
                mindmapNodes: nodes.get(), mindmapEdges: edges.get()
            };
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sessionData));
            const a = document.createElement('a');
            a.setAttribute("href", dataStr);
            a.setAttribute("download", "manuscript_session.aws");
            document.body.appendChild(a); 
            a.click(); a.remove();
        }

        function importSession(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = JSON.parse(e.target.result);
                    if (data.editor) { document.getElementById('editor').innerHTML = data.editor; updateTOC(); }
                    if (data.pdfNotes) document.querySelector('.pdf-notes').innerHTML = data.pdfNotes;
                    if (data.mindmapNodes && data.mindmapEdges) {
                        if(!network) initMindmap();
                        nodes.clear(); edges.clear();
                        nodes.add(data.mindmapNodes); edges.add(data.mindmapEdges);
                        switchTab('mindmap'); setTimeout(() => { network.fit(); }, 100);
                    }
                } catch(err) { alert("Invalid .aws file format."); }
            };
            reader.readAsText(file);
        }
    </script>
</body>
</html>
"""

# --- FLASK ROUTES ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/grammar_local', methods=['POST'])
def grammar_local():
    text = request.json.get('text', '')
    issues = []
    
    doubles = re.finditer(r'\b(\w+)\s+\1\b', text, re.IGNORECASE)
    for match in doubles:
        issues.append({"type": "Duplication", "match": match.group(0), "suggestion": f"Remove the extra '{match.group(1)}'"})
        
    wordy_phrases = { r'\bdue to the fact that\b': 'because', r'\ba majority of\b': 'most', r'\bin order to\b': 'to' }
    for pattern, suggestion in wordy_phrases.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            issues.append({"type": "Wordiness", "match": match.group(0), "suggestion": suggestion})

    # --- Human-like Academic Tone Checker ---
    robotic_phrases = {
        r'\bit is observed that\b': 'we observed that',
        r'\bthe utilization of\b': 'using',
        r'\bit is evident that\b': 'clearly,',
        r'\bhas the capability to\b': 'can',
        r'\bfor the purpose of\b': 'to',
        r'\baforementioned\b': 'previously mentioned',
        r'\belucidate\b': 'explain / clarify',
        r'\bameliorate\b': 'improve',
        r'\bthere is a need for\b': 'we must / it is necessary to'
    }
    for pattern, suggestion in robotic_phrases.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            issues.append({"type": "Robotic/Clunky Tone", "match": match.group(0), "suggestion": suggestion})

    return jsonify(issues)

@app.route('/api/synonyms', methods=['GET'])
def get_synonyms():
    word = request.args.get('word', '').strip()
    if not word: return jsonify({"synonyms": []})
    
    # Advanced morphological tense extraction
    base_word = word.lower()
    suffix = ""
    
    if base_word.endswith("ing"):
        base_word_stem = lemmatizer.lemmatize(base_word, pos='v')
        suffix = "ing"
    elif base_word.endswith("ed"):
        base_word_stem = lemmatizer.lemmatize(base_word, pos='v') 
        suffix = "ed"
    elif base_word.endswith("ly"):
        base_word_stem = base_word[:-2]
        suffix = "ly"
    elif base_word.endswith("s") and not base_word.endswith("ss"):
        base_word_stem = lemmatizer.lemmatize(base_word, pos='n')
        suffix = "s"
    else:
        base_word_stem = base_word

    synonyms = set()
    # Fetch extensive synonyms
    for syn in wordnet.synsets(base_word_stem):
        for lemma in syn.lemmas():
            clean_word = lemma.name().replace('_', ' ').lower()
            if clean_word != base_word_stem and clean_word != base_word:
                # Re-apply tense/morphology mathematically
                if suffix == "ing":
                    if clean_word.endswith("e"): clean_word = clean_word[:-1] + "ing"
                    else: clean_word += "ing"
                elif suffix == "ed":
                    if clean_word.endswith("e"): clean_word += "d"
                    else: clean_word += "ed"
                elif suffix == "ly":
                    clean_word += "ly"
                elif suffix == "s":
                    if not clean_word.endswith("s"): clean_word += "s"
                
                # Match original capitalization
                if word.istitle():
                    clean_word = clean_word.title()
                
                synonyms.add(clean_word)
    
    # Return a much larger pool of synonyms
    return jsonify({"synonyms": list(synonyms)[:25]})

@app.route('/api/search', methods=['POST'])
def search_literature():
    """
    Robust API requests utilizing multi-tier fallbacks and browser-mimicking headers.
    """
    data = request.json
    query = data.get('query', '')
    source = data.get('source', 'openalex')
    try:
        count = int(data.get('count', 10))
    except ValueError:
        count = 10
        
    results = []
    
    # Use highly standard browser headers to bypass strict APIs like Semantic Scholar
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

    try:
        if source == 'google':
            # Google Scholar scraping implementation using BeautifulSoup
            safe_query = urllib.parse.quote_plus(query)
            url = f"https://scholar.google.com/scholar?q={safe_query}&num={count}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for item in soup.select('[data-lid]')[:count]:
                    title_elem = item.select_one('.gs_rt a')
                    if not title_elem:
                        title_elem = item.select_one('.gs_rt')
                    title = title_elem.text if title_elem else "Untitled"
                    link = title_elem['href'] if title_elem and title_elem.has_attr('href') else "#"
                    
                    author_year_elem = item.select_one('.gs_a')
                    authors = "Unknown"
                    year = "N/A"
                    if author_year_elem:
                        author_year_text = author_year_elem.text
                        parts = author_year_text.split('-')
                        if len(parts) > 0:
                            authors = parts[0].strip()
                        year_match = re.search(r'\b(19|20)\d{2}\b', author_year_text)
                        if year_match:
                            year = year_match.group(0)
                            
                    results.append({
                        "title": title,
                        "authors": authors[:60] + ("..." if len(authors)>60 else ""),
                        "year": year,
                        "link": link
                    })
            else:
                print(f"Google Scholar Error: HTTP {res.status_code}")

        elif source == 'semantic':
            # Semantic Scholar Specific Crawler (2-Tier System)
            safe_query = urllib.parse.quote(query)
            session = requests.Session()
            
            # Attempt 1: Official Graph API
            api_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={safe_query}&limit={count}&fields=title,authors,year,url"
            res = session.get(api_url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                for work in data.get('data', []):
                    authors = ", ".join([a.get('name', '') for a in work.get('authors', [])][:3])
                    results.append({
                        "title": work.get('title', 'Untitled'),
                        "authors": authors + " et al." if authors else "Unknown",
                        "year": str(work.get('year', 'N/A')),
                        "link": work.get('url', f"https://www.semanticscholar.org/paper/{work.get('paperId', '')}")
                    })
            else:
                # Attempt 2: Internal Frontend API (Acts exactly like a user searching on their website)
                web_url = "https://www.semanticscholar.org/api/1/search"
                payload = {"queryString": query, "page": 1, "pageSize": count, "sort": "relevance"}
                web_res = session.post(web_url, json=payload, headers=headers, timeout=10)
                if web_res.status_code == 200:
                    data = web_res.json()
                    for work in data.get('results', []):
                        title_data = work.get('title', {})
                        title = title_data.get('text', 'Untitled') if isinstance(title_data, dict) else str(title_data)
                        
                        auth_list = []
                        for author_obj in work.get('authors', [])[:3]:
                            if isinstance(author_obj, list) and len(author_obj) > 0:
                                auth_list.append(author_obj[0].get('name', ''))
                            elif isinstance(author_obj, dict):
                                auth_list.append(author_obj.get('name', ''))
                        authors = ", ".join(auth_list)
                        
                        year_data = work.get('year', {})
                        year = str(year_data.get('text', 'N/A')) if isinstance(year_data, dict) else str(year_data)
                        
                        link = f"https://www.semanticscholar.org/paper/{work.get('id', '')}"
                        results.append({
                            "title": title,
                            "authors": authors + " et al." if authors else "Unknown",
                            "year": year,
                            "link": link
                        })

        elif source == 'arxiv':
            safe_query = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{safe_query}&max_results={count}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns)[:count]:
                    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                    authors = ", ".join([a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)])
                    year = entry.find('atom:published', ns).text[:4] if entry.find('atom:published', ns) is not None else "N/A"
                    link = entry.find('atom:id', ns).text
                    results.append({"title": title, "authors": authors[:60]+"...", "year": year, "link": link})
                
        elif source == 'crossref':
            safe_query = urllib.parse.quote_plus(query)
            url = f"https://api.crossref.org/works?query={safe_query}&rows={count}&select=title,author,issued,URL"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('message', {}).get('items', []):
                    title = item.get('title', ['Unknown'])[0]
                    authors = ", ".join([f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get('author', [])])
                    year = str(item['issued']['date-parts'][0][0]) if 'issued' in item and 'date-parts' in item['issued'] else "Unknown"
                    results.append({"title": title, "authors": authors[:60]+"...", "year": year, "link": item.get('URL', '#')})
                
        elif source == 'openalex':
            safe_query = urllib.parse.quote(query)
            url = f"https://api.openalex.org/works?search={safe_query}&per-page={count}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                for work in data.get('results', []):
                    authors = ", ".join([a['author']['display_name'] for a in work.get('authorships', [])][:3])
                    results.append({
                        "title": work.get('title', 'Untitled'),
                        "authors": authors + " et al." if authors else "Unknown",
                        "year": str(work.get('publication_year', 'N/A')),
                        "link": work.get('id', '#')
                    })
                
    except Exception as e:
        print(f"API Fetch error: {e}")
        pass 
        
    return jsonify(results)


def extract_academic_noun_phrases(text):
    """
    Custom POS-based extractor:
    Scans the text and forces the algorithm to ONLY extract multi-word conceptual phrases
    (e.g. Adjective + Noun + Noun). This prevents generic terms like "street" or "data".
    """
    sentences = nltk.sent_tokenize(text)
    academic_phrases = []
    
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence.lower())
        pos_tags = nltk.pos_tag(tokens)
        
        current_phrase = []
        for word, tag in pos_tags:
            # If the word is an Adjective or Noun, add it to the current phrase chain
            if word.isalpha() and len(word) > 2 and (tag.startswith('JJ') or tag.startswith('NN')):
                current_phrase.append(word)
            else:
                # Chain broken. If we collected 2 or more words, it's a valid concept.
                if len(current_phrase) >= 2:
                    # Join with underscores so TF-IDF treats it as a single mathematical feature
                    academic_phrases.append("_".join(current_phrase))
                current_phrase = []
                
        # Catch any trailing phrases at the end of a sentence
        if len(current_phrase) >= 2:
            academic_phrases.append("_".join(current_phrase))
            
    return academic_phrases


@app.route('/api/analyze_pdfs', methods=['POST'])
def analyze_pdfs():
    """
    Enhanced NLP approach utilizing custom Noun Phrase extraction to capture
    highly specific, complex academic topics instead of generic single words.
    """
    try:
        import PyPDF2
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
    except ImportError:
        return jsonify({"error": "Missing libraries. Please run: pip install PyPDF2 scikit-learn numpy"}), 400

    try:
        files = request.files.getlist('pdfs')
        if not files: return jsonify({"error": "No PDFs received."}), 400

        raw_texts, clean_phrases_texts, titles = [], [], []
        import io
        
        for f in files:
            try:
                file_stream = io.BytesIO(f.read())
                reader = PyPDF2.PdfReader(file_stream)
                text = " ".join([reader.pages[p].extract_text() for p in range(min(len(reader.pages), 30)) if reader.pages[p].extract_text()])
                
                if text.strip():
                    raw_texts.append(text)
                    titles.append(f.filename)
                    
                    # Run the strict Noun-Phrase extractor
                    phrases = extract_academic_noun_phrases(text)
                    clean_phrases_texts.append(" ".join(phrases))
                    
            except Exception as e: 
                print(f"Skipping file {f.filename} due to extraction error: {e}")
                pass

        if not raw_texts: return jsonify({"error": "Could not extract text from the provided PDFs. They might be image-based."}), 400
        if not any(clean_phrases_texts): return jsonify({"error": "Could not extract meaningful academic concepts from the text."}), 400

        nodes, edges = [], []
        
        gap_keywords = ['gap in', 'lack of', 'overlooked', 'scarcity', 'remains unclear', 'little attention', 'future research', 'limitation', 'however, no', 'fail to', 'unexplored']

        # We configure TF-IDF to use the exact underscored phrases we constructed
        vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', max_features=200)
        
        try:
            tfidf_matrix = vectorizer.fit_transform(clean_phrases_texts)
            feature_names = vectorizer.get_feature_names_out()
        except ValueError:
            return jsonify({"error": "Vocabulary extraction failed. Documents may be too short."}), 400

        for i, title in enumerate(titles):
            short_title = title[:20] + "..." if len(title)>20 else title
            doc_id = f"doc_{i}"
            nodes.append({"id": doc_id, "label": short_title, "shape": "box", "color": "#bae6fd", "title": title})

            # Extract Contextual Research Gaps
            try:
                sentences = nltk.sent_tokenize(raw_texts[i].replace('\n', ' '))
                for s in sentences:
                    s_lower = s.lower()
                    for k in gap_keywords:
                        if k in s_lower:
                            # Isolate the specific clause (instead of returning the whole massive sentence)
                            idx = s_lower.find(k)
                            snippet = s[max(0, idx-5):idx+55].strip() + "..."
                            gap_id = f"gap_{i}"
                            label_text = snippet.replace(k, k.upper())
                            
                            nodes.append({"id": gap_id, "label": f"Identified Gap:\n{label_text}", "shape": "diamond", "color": "#fecaca", "title": s})
                            edges.append({"from": doc_id, "to": gap_id, "label": "Identifies", "color": "#ef4444", "dashes": True})
                            break # Found one gap per document
                    else:
                        continue
                    break
            except Exception: pass

        # Explicit Similarities and Differences Analysis
        if len(clean_phrases_texts) > 1:
            sim_matrix = cosine_similarity(tfidf_matrix)
            for i in range(len(clean_phrases_texts)):
                for j in range(i+1, len(clean_phrases_texts)):
                    sim = sim_matrix[i][j]
                    
                    row_i = tfidf_matrix.getrow(i).toarray()[0]
                    row_j = tfidf_matrix.getrow(j).toarray()[0]
                    
                    # Shared Focus extraction
                    if sim > 0.05: 
                        overlap = row_i * row_j
                        best_overlap_idx = np.argmax(overlap)
                        if overlap[best_overlap_idx] > 0.005:
                            # Revert underscores to spaces for elegant display
                            shared_term = feature_names[best_overlap_idx].replace('_', ' ').title()
                            term_id = f"sim_{shared_term.replace(' ','_')}"
                            
                            if not any(n['id'] == term_id for n in nodes):
                                nodes.append({"id": term_id, "label": f"Shared Focus:\n{shared_term}", "shape": "ellipse", "color": "#bbf7d0", "title": f"Common semantic theme (Similarity: {sim:.2f})"})
                            
                            edges.append({"from": f"doc_{i}", "to": term_id, "label": "Explores", "color": "#22c55e"})
                            edges.append({"from": f"doc_{j}", "to": term_id, "label": "Explores", "color": "#22c55e"})

                    # Differentiating Insight Extraction (Absolute Absence Logic on Specific Phrases)
                    max_diff_i, unique_to_i_idx = 0, -1
                    for idx in range(len(feature_names)):
                        if row_i[idx] > 0.15 and row_j[idx] == 0: 
                            if row_i[idx] > max_diff_i:
                                max_diff_i = row_i[idx]
                                unique_to_i_idx = idx

                    if unique_to_i_idx != -1: 
                        unique_term_i = feature_names[unique_to_i_idx].replace('_', ' ').title()
                        term_id = f"diff_{i}_{unique_term_i.replace(' ','_')}"
                        if not any(n['id'] == term_id for n in nodes):
                            nodes.append({"id": term_id, "label": f"Unique Insight:\n{unique_term_i}", "shape": "hexagon", "color": "#fed7aa", "title": f"Concept localized to {titles[i]}"})
                        edges.append({"from": f"doc_{i}", "to": term_id, "label": "Differentiates by focusing on", "color": "#f97316", "width": 2})
                        
                    max_diff_j, unique_to_j_idx = 0, -1
                    for idx in range(len(feature_names)):
                        if row_j[idx] > 0.15 and row_i[idx] == 0:
                            if row_j[idx] > max_diff_j:
                                max_diff_j = row_j[idx]
                                unique_to_j_idx = idx

                    if unique_to_j_idx != -1: 
                        unique_term_j = feature_names[unique_to_j_idx].replace('_', ' ').title()
                        term_id = f"diff_{j}_{unique_term_j.replace(' ','_')}"
                        if not any(n['id'] == term_id for n in nodes):
                            nodes.append({"id": term_id, "label": f"Unique Insight:\n{unique_term_j}", "shape": "hexagon", "color": "#fed7aa", "title": f"Concept localized to {titles[j]}"})
                        edges.append({"from": f"doc_{j}", "to": term_id, "label": "Differentiates by focusing on", "color": "#f97316", "width": 2})

        return jsonify({"nodes": nodes, "edges": edges})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server processing error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Academic Writing Studio...")
    app.run(debug=True, port=5000, use_reloader=False)