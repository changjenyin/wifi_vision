function signal = subcarrier_norm(signal)
	[w h] = size(signal);
	for idx = 1:w
		%Translate to mean=0
		signal(idx, :) = signal(idx, :) - mean(signal(idx, :));

		%Normalize to 0~255
		min_sig = min(signal(idx, :));
		max_sig = max(signal(idx, :));
		signal(idx, :) = ((signal(idx, :) - repmat(min_sig, 1, h)) ./ repmat(max_sig - min_sig, 1, h)) * 255;

		%min_sig = min(signal(idx, :));
		%max_sig = max(signal(idx, :));
		%signal(idx, :) = (signal(idx, :) - repmat(min_sig, 1, h)) ./ repmat(max_sig - min_sig, 1, h);
	end
end
