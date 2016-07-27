function parse_csi(folder, root_dir, power, interp_interval, sec)
	addpath('/tmp4/transfer/WiSee/linux-80211n-csitool-supplementary/matlab');
	start_idx = 100;
	num_sub 	= 30
	sz = 120;

	% Interval: micro-second
	if ~exist('interp_interval', 'var')
		interp_interval = 1000;
	end
	% sec: recorded seconds
	if ~exist('sec', 'var')
		sec = 5;
	end

	if power == 1
		disp 'Using power'
	else
		disp 'Using amp.'
	end

	files = dir([folder '/*.bin']);
	for file = files'
		names = strsplit(file.name, '.');
		name = names(1);
		%if ~strcmp(name, 'still10')
		%	continue
		%end
		%if ~strcmp(name,'run17')
		%	continue
		%end
		name
	
		csi_mat = [];
		ori_timestamp = [];
		csi_trace = read_bf_file([folder '/' file.name]);
	
		interp_csi = csi_interpolation(name, csi_trace, interp_interval, sec, power);
		continue;


		%input('interp_csi size')
		if interp_csi == 0
			continue
		end

		action_dir = cell2mat([root_dir '/' name])
		if ~exist(action_dir, 'dir')
			mkdir(action_dir);
		end

		% STFT
		addpath('/tmp4/transfer/WiSee/csi');
		addpath('/tmp4/transfer/WiSee/csi/dataplot');

		pca_H = pca(action_dir, interp_csi');
		fig = figure(1); clf;
		for i = 1:5
			subplot(5, 1, i);
			plot(pca_H(i,:));
		end
		save_path = [action_dir '/pca_2.jpg'];
		saveas(fig, save_path);

		clf;
		for i = 1:5
			subplot(5, 1, i);
			plot(interp_csi(i,:));
		end
		save_path = [action_dir '/sub1-5.jpg'];
		saveas(fig, save_path);
		% STFT


		fids = [fopen([action_dir '/1.ant'], 'w'), fopen([action_dir '/2.ant'], 'w'), fopen([action_dir '/3.ant'], 'w') fopen([action_dir '/4.ant'], 'w'), fopen([action_dir '/avg'], 'w'), fopen([action_dir '/all'], 'w')];

		avg = zeros(sz/num_sub, size(interp_csi, 2));
		for row = 1:size(interp_csi, 1) 
			fid_idx = ceil(row / num_sub);
			fprintf(fids(fid_idx), '%g ', interp_csi(row, :));
			fprintf(fids(fid_idx), '\n');

			% All sub in one file
			fprintf(fids(end), '%g ', interp_csi(row, :));
			fprintf(fids(end), '\n');

			avg(fid_idx, :) = avg(fid_idx, :) + interp_csi(row, :);
		end

		for idx = 1:size(avg, 1)
			fprintf(fids(end-1), '%g ', avg(idx, :)/num_sub);
			fprintf(fids(end-1), '\n');
		end

		for idx = 1:size(fids,2)
			fclose(fids(idx));
		end
	end
end
