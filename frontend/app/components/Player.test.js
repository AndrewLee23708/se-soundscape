import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import Player from './Player';

describe('Player Component', () => {
  it('renders playback controls', () => {
    const { getByTestId } = render(<Player />);
    expect(getByTestId('play-pause-btn')).toBeInTheDocument();
  });

  it('toggles play/pause on click', () => {
    const handlePlayPause = jest.fn();
    const { getByTestId } = render(<Player onPlayPause={handlePlayPause} />);
    const playPauseButton = getByTestId('play-pause-btn');
    fireEvent.click(playPauseButton);
    expect(handlePlayPause).toHaveBeenCalled();
  });
