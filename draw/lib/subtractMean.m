function signal = subtractMean(signal)
	mean_list = mean(signal, 2);
	mean_list = repmat(mean_list, 1, size(signal, 2));
	signal = signal - mean_list;
end
