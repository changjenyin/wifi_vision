function parse_csi(folder, root_dir, power, interp_interval, sec)
	%addpath('/tmp4/transfer/WiSee/linux-80211n-csitool-supplementary/matlab');
	addpath('../../../linux-80211n-csitool-supplementary/matlab');
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

	files = dir([folder '/*.bin'])
	for file = files'
		names = strsplit(file.name, '.');
		name = names(1);
		%if ~strcmp(name,'run17')
		%	continue
		%end
	
		csi_mat = [];
		ori_timestamp = [];
		csi_trace = read_bf_file([folder '/' file.name]);
		size(csi_trace)
	
		for idx = start_idx:size(csi_trace, 1)
			csi = csi_trace{idx}.csi;
			%TODO: draw four graphs for four antennas

			% Find the permutation of Rx ants
			ant_1st = find(csi_trace{idx}.perm == 1);
			ant_2nd = find(csi_trace{idx}.perm == 2);
			%csi_trace{idx}
			%abs(csi(:,:,30))
			%input('hehe')
	
			% When there are 2*3 Tx-Rx ants pairs
			% Pick 1*3 pairs where abs of two Tx ants are closer
			shape = size(csi, 1)*size(csi, 2)*size(csi,3);
			if shape ~= 180 && shape ~= 120
				continue 
				idx_1 = abs(abs(csi(1,ant_1st,1)) - abs(csi(1,ant_2nd,1)));
				idx_2 = abs(abs(csi(2,ant_1st,1)) - abs(csi(2,ant_2nd,1)));
				if idx_1 > idx_2
					csi = csi(2,:,:);
				else
					csi = csi(1,:,:);
				end
			end 

			ori_timestamp = [ori_timestamp, csi_trace{idx}.timestamp_low];

			% Transform into a column vector with subcarriers of the same ant pair together (30*n)*1
			csi = reshape(csi(:,[ant_1st, ant_2nd],:), 4, sz/4);
			csi = reshape(csi', sz, 1);
			csi_mat = [csi_mat, csi];
		end
		size(csi_mat)
		ori_timestamp = ori_timestamp - ori_timestamp(1);

		% Check the number of duplicate timestamp
		% and remove all duplicated samples
		curr_timestamp = ori_timestamp(1, 1);
		idx = [];
		cnt = 0;
		for i = 2:size(ori_timestamp, 2)
				if ori_timestamp(1,i) == curr_timestamp
					idx = [idx, i];
					cnt = cnt + 1;
				end
				curr_timestamp = ori_timestamp(1,i);
		end
		disp 'duplicated number:'  
		disp (cnt)

		csi_mat(:,idx) = [];
		ori_timestamp(:,idx) = [];

		% Do interpolation to 1000 CSI/s
		action_dir = cell2mat([root_dir '/' name])
		if ~exist(action_dir, 'dir')
			mkdir(action_dir);
		end

		fids = [fopen([action_dir '/1.ant'], 'w'), fopen([action_dir '/2.ant'], 'w'), fopen([action_dir '/3.ant'], 'w') fopen([action_dir '/4.ant'], 'w'), fopen([action_dir '/avg'], 'w')];

		new_timestamp = interp_interval:interp_interval:min(sec * 10^6, ori_timestamp(end));
		avg = zeros(sz/num_sub, size(new_timestamp, 2));
		for row = 1:size(csi_mat, 1) 
			% complex number with no interpolation
			%ori_mat = csi_mat(row,:)
			if power == 1
				ori_mat = abs(csi_mat(row,:)).^2;
			else
				ori_mat = abs(csi_mat(row,:));
			end

			% Interpolate to the end of timestamp
			%ori_timestamp(end)
			%input('hi', 's')
			interp_mat = interp1(ori_timestamp,ori_mat,new_timestamp);

			fid_idx = ceil(row / num_sub);
			fprintf(fids(fid_idx), '%g ', interp_mat);
			%fprintf(fids(fid_idx), '%g%g ', real(ori_mat), imag(ori_mat));
			%fprintf(fids(fid_idx), '\n');

			avg(fid_idx, :) = avg(fid_idx, :) + interp_mat;
			%avg(fid_idx, :) = avg(fid_idx, :) + ori_mat;
		end
		for idx = 1:size(avg, 1)
			fprintf(fids(end), '%g ', avg(idx, :)/num_sub);
			fprintf(fids(end), '\n');
		end

		for idx = 1:size(fids,2)
			fclose(fids(idx));
		end
	end
end
