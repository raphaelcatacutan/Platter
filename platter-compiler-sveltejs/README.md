# Platter IDE Frontend

A SvelteKit-based IDE for the Platter programming language, using a FastAPI backend for analysis and execution.

## Features

- **Lexical Analysis**: Tokenize Platter code
- **Syntax Analysis**: Parse and validate Platter syntax
- **Code Editor**: CodeMirror integration with syntax highlighting
- **Error Highlighting**: Visual error markers in the editor
- **Dark/Light Theme**: Toggle between themes
- **File Operations**: Open and save `.platter` files
- **Backend Execution**: Runs analysis and IR interpreter on the FastAPI server

## Developing

Install dependencies and start the development server:

```sh
npm install
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

The app will be available at `http://localhost:5173`

Start the backend in a separate terminal:

```sh
cd ../backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

## Deployment

The frontend can be deployed as static assets, but the FastAPI backend must also be hosted.

## Python Integration

Python code under `static/python/app/` is used by the FastAPI backend for analysis:

- `app.lexer.*` - Lexical analysis
- `app.parser.*` - Syntax analysis

## Technical Stack

- **Framework**: SvelteKit
- **Styling**: Tailwind CSS
- **Editor**: CodeMirror 5
- **Backend**: FastAPI + Uvicorn
- **Build Tool**: Vite
