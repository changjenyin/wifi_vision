function low_avg(folder, output_folder, width, height, NUM_ANT_PAIR)
	if ~exist('NUM_ANT_PAIR', 'var')
		NUM_ANT_PAIR = 4;
	end

	SUB_CNT 	  = NUM_ANT_PAIR*30;
	time  		  = 5;
	target_freq   = 50;
	avg_window_ms = 300;

	parts = strsplit(folder, '/');

	dirlist = dir(folder);
	SV = []; names = {};

	vmins = {[],[],[],[]}; vmaxs = {[],[],[],[]};
	new_H_min  = repmat(Inf, 1, 4); new_H_max  = repmat(-Inf, 1, 4);
	for i = 3:length(dirlist)
		filename = dirlist(i).name

		parts = strsplit(filename, '.');
		names{end+1} = parts(1);
		if strcmp(filename, 'all') || strcmp(filename, 'avg')
			continue
		end

		load([folder '/' filename]);
		H = ori_mat;

	    % Signal conditioning and Low-pass
		num_point_s  = floor(size(H, 2) / time);
		avg_window_pt = floor(num_point_s / (1000/avg_window_ms));

		new_H = avg_window(avg_window_pt, H);
		new_H = low_pass(num_point_s, target_freq, H);

		new_H = new_H.';
		isComplex = ~isreal(new_H);
		for i = 1:NUM_ANT_PAIR
			result = new_H(:, (i - 1) * 30 + 1:i * 30);
			if isComplex
				vmin = min(min(min(abs(result))));
				vmax = max(max(max(abs(result))));
			else
				vmin = min(min(min(result)));
				vmax = max(max(max(result)));
			end
			vmins{i} = [vmins{i}, vmin]; 
			vmaxs{i} = [vmaxs{i}, vmax]; 
			
			if vmin < new_H_min(1, i)
				new_H_min(1, i) = vmin;
			end

			if vmax > new_H_max(1, i)
				new_H_max(1, i) = vmax;
			end
		end
	end

	for i = 3:length(dirlist)
		filename = dirlist(i).name
		% Ignore other files
		if strcmp(filename, 'all') || strcmp(filename, 'avg')
			continue
		end
		
		% Read in H as t x SUB_CNT
		load([folder '/' filename]);
		H = ori_mat;
		
		% Output for training
		action = strsplit(filename, '.');
		mkdir([output_folder '/' action{1}]);

	    % Signal conditioning and Low-pass
		num_point_s  = floor(size(H, 2) / time);
		avg_window_pt = floor(num_point_s / (1000/avg_window_ms));
		new_H = avg_window(avg_window_pt, H);
		new_H = low_pass(num_point_s, target_freq, H);

		new_H = new_H.';

		cf = 1;
		for i = 1:NUM_ANT_PAIR
			img = figure(cf);
			if isComplex
				result = image(abs(new_H(:, (i - 1) * 30 + 1:i * 30)), 'CDataMapping', 'scaled');
			else
				result = image(new_H(:, (i - 1) * 30 + 1:i * 30), 'CDataMapping', 'scaled');
			end
			%result = image(new_H(:, (i - 1) * 30 + 1:i * 30), 'CDataMapping', 'scaled');
		    set(gca, 'position', [0 0 1 1], 'units', 'normalized');
			set(gca, 'CLim', [new_H_min(1, i), new_H_max(1, i)]);
		    axis off;
			res = get(0, 'screenpixelsPerInch');
			pSize = [width, height] / res;
		    set(gcf,'PaperUnits','inches')
			set(gcf,'PaperSize', pSize)
			set(gcf,'PaperPosition',[1 1 pSize(1) pSize(2)]);
			set(gcf,'PaperPositionMode', 'manual')
		    print('-djpeg', [output_folder '/' action{1} '/' num2str(i)], sprintf('-r%d', res));

			clf;
			cf = cf + 1;
		end
	end
end

function low_passed = low_pass(sample_f, cutoff_f, signal)
	sub_cnt = size(signal, 1);
	butter_f = cutoff_f / (sample_f / 2);
	[a, b] = butter(5, butter_f, 'low');
	for i=1:sub_cnt
	    low_passed(i, :) = filter(a, b, sqrt(2) * abs(signal(i, :)));
	end
end

function signal_new = avg_window(sz, signal)
	sub_cnt = size(signal, 1);
	signal_new = zeros(size(signal));

	for idx = 1:sub_cnt
	    sub_avg = 0;
	    for i = 1:size(signal, 2) - 1 
	        if i - sz < 1
	            sub_avg = (sub_avg * (i - 1) + signal(idx, i)) / i;
	        else
	            sub_avg = sub_avg + (signal(idx, i) - signal(idx, i - sz)) / sz;
	        end
	        signal_new(idx, i + 1) = signal(idx, i + 1) - sub_avg;
	    end
	end
end
