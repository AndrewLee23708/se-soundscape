import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import Map from '../components/Map'; // Adjust the import path as per your project structure
import '@testing-library/jest-dom/extend-expect';
import { Loader } from '@googlemaps/js-api-loader';

// Mock necessary modules and globals
jest.mock('@googlemaps/js-api-loader', () => ({
  Loader: jest.fn().mockImplementation(() => ({
    load: jest.fn(() => Promise.resolve({
      maps: {
        Map: jest.fn().mockImplementation(() => ({
          setCenter: jest.fn(),
          addListener: jest.fn(),
        })),
        LatLng: jest.fn(),
        Marker: jest.fn(),
        Circle: jest.fn(),
        InfoWindow: jest.fn(),
      }
    })),
  }))
}));

// Mock fetch for API interactions
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ google_api_key: 'fake_key' }),
  })
);

describe('Map Component Tests', () => {
  beforeEach(() => {
    fetch.mockClear();
    Loader.mockClear();
  });

  it('initializes the map with default settings', async () => {
    const { findByText } = render(<Map />);
    await waitFor(() => {
      expect(Loader).toHaveBeenCalled();
      expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:5000/googlekey');
    });
    expect(await findByText('Location')).toBeInTheDocument();
  });

  it('toggles marker state on button click', async () => {
    const { getByText } = render(<Map />);
    const markerButton = getByText('Marker');
    fireEvent.click(markerButton);
    await waitFor(() => {
      expect(markerButton).toHaveClass('btn btn-primary');
    });
    fireEvent.click(markerButton);
    await waitFor(() => {
      expect(markerButton).toHaveClass('btn btn-outline-primary');
    });
  });

  it('fetches pins successfully from the API', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          pins: [{ id: 1, name: "Test Pin", lat: -77.0364, lng: 38.8951 }]
        })
      })
    );
    const { findByText } = render(<Map />);
    expect(await findByText('Test Pin')).toBeInTheDocument();
  });

  it('handles map click to create a new pin', async () => {
    const { getByText } = render(<Map />);
    const locationButton = getByText('Location');
    fireEvent.click(locationButton);
    // Assume maps.MouseEvent returns LatLng object with lat/lng
    const mapsMouseEvent = { latLng: { lat: () => 38.8951, lng: () => -77.0364 } };
    const addListenerMock = jest.fn().mockImplementation((event, cb) => {
      if (event === 'click') cb(mapsMouseEvent);
    });
    const mapMock = {
      setCenter: jest.fn(),
      addListener: addListenerMock,
    };
    await waitFor(() => {
      expect(addListenerMock).toHaveBeenCalledWith('click', expect.any(Function));
    });
  });
});
