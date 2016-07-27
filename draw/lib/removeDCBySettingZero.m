function signal = removeDCBySettingZero(signal) 
	[w h] = size(signal);

	fft_result = ifft(signal, w, 1);

	fig = figure();
	for idx = 1:30
		subplot(10, 3, idx);
		abs(fft_result(:,idx));
		plot(abs(fft_result(:, idx)));
	end
	saveas(fig, 'ifft_result.jpg')

	[col_max, idx] = max(fft_result, [], 1);

	% Set the first-arriving signal to be zero (Should be LOS)
	for col = 1:h
		row = idx(col);
		fft_result(row, col) = 0;
	end

	% Transfrom back to frequency domain
	signal = fft(fft_result, w, 1);
end

