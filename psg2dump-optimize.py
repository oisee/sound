import argparse

REG_NUM = 14

def read_aydump_file(filename):
    frames = []
    with open(filename, 'r') as file:
        for line in file:
            frame = []
            for value in line.strip().split('\t'):
                if value == '_':
                    frame.append(None)
                else:
                    frame.append(int(value))
            frames.append(frame)
    return frames

def optimize_frames(frames):
    optimized_frames = []
    previous_frame = [None] * REG_NUM

    for frame in frames:
        optimized_frame = []
        for reg, value in enumerate(frame):
            if reg == 13:
                optimized_frame.append(value)
            elif value is not None and value == previous_frame[reg]:
                optimized_frame.append(None)
            else:
                optimized_frame.append(value)
        optimized_frames.append(optimized_frame)
        previous_frame = frame

    return optimized_frames

def write_register_dump(frames, output_filename):
    with open(output_filename, 'w') as file:
        for frame in frames:
            output_frame = []
            for value in frame:
                if value is None:
                    output_frame.append('_')
                else:
                    output_frame.append(str(value))
            file.write('\t'.join(output_frame) + '\n')

def main(input_filename, output_filename):
    frames = read_aydump_file(input_filename)
    optimized_frames = optimize_frames(frames)
    write_register_dump(optimized_frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optimize AY register dump by replacing unchanged values with "_".')
    parser.add_argument('input_filename', nargs='?', default='sync.psg.aydump', help='The input AY register dump file (default: sync.psg.aydump)')
    parser.add_argument('output_filename', nargs='?', help='The output optimized AY register dump file (default: input_filename.opt.aydump)')
    args = parser.parse_args()
    
    input_filename = args.input_filename
    output_filename = args.output_filename if args.output_filename else input_filename + '.opt.aydump'
    
    main(input_filename, output_filename)
