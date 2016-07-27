function signal = removeDCBySubtractMean(signal) 
	empty_section = 1:100;
	[w h] = size(signal);

	fft_result = ifft(signal, w, 1);
	mean_taps  = mean(abs(fft_result(:, empty_section)), 2);

	for col = 1:h
		row = idx(col);
		fft_result(row, col) = 0;
	end
	signal = fft(fft_result, w, 1);
end
