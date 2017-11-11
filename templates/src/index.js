require('babel-polyfill');
import React from 'react';
import ReactDOM from 'react-dom';
import App from './app/App';

document.addEventListener('DOMContentLoaded', () => {
  ReactDOM.render(
    <App name="App"/>,
    document.body.appendChild(document.createElement('div'))
  )
});
