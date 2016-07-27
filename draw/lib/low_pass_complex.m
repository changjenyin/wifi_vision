function low_passed = low_pass(sample_f, cutoff_f, signal)
	sub_cnt = size(signal, 1);
	butter_f = cutoff_f / (sample_f / 2);
	[a, b] = butter(5, butter_f, 'low');
	for i=1:sub_cnt
	    low_passed(i, :) = filter(a, b, sqrt(2) * signal(i, :));
	end
end
