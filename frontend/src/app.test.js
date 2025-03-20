import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom'
import axios from 'axios';
import App from './app';

jest.mock('axios'); // Mock axios for API calls

describe('App Component', () => {
  beforeEach(() => {
    axios.get.mockReset();
    axios.post.mockReset();
  });

  it('renders upload interface and transcription list', () => {
    render(<App />);
    expect(screen.getByText('Audio Transcription App')).toBeInTheDocument();
    expect(screen.getByText('Upload Audio File(s)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
    expect(screen.getByText('Transcriptions')).toBeInTheDocument();
  });

  it('uploads files and updates transcription list', async () => {
    const mockFiles = [new File(['audio'], 'test.mp3', { type: 'audio/mp3' })];
    const mockTranscriptions = [{ audio_filename: 'test.mp3', transcribed_text: 'test transcription', created_at: '2025-01-01 08:58:30.543544' }];

    axios.post.mockResolvedValue({}); // Mock successful upload
    axios.get.mockResolvedValue({ data: mockTranscriptions }); // Mock successful fetch

    render(<App />);
    const fileInput = screen.getByTestId('file-upload-input');
    fireEvent.change(fileInput, { target: { files: mockFiles } });
    fireEvent.click(screen.getByText('Upload'));

    await waitFor(() => {
      mockTranscriptions.forEach(obj => {
        Object.values(obj).forEach(txt => {
          expect(screen.getByText(txt)).toBeInTheDocument();
        });
      });
    });
  });

  it('searches for transcriptions by filename', async () => {
    const mockTranscriptions = [{ audio_filename: 'search.mp3', transcribed_text: 'search transcription', created_at: '2025-02-02 02:52:32.543544' }];

    axios.get.mockResolvedValue({ data: mockTranscriptions }); // Mock successful search

    render(<App />);
    const searchInput = screen.getByPlaceholderText('Search by filename');
    fireEvent.change(searchInput, { target: { value: 'search' } });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      mockTranscriptions.forEach(obj => {
        Object.values(obj).forEach(txt => {
          expect(screen.getByText(txt)).toBeInTheDocument();
        });
      });
    });
  });
});