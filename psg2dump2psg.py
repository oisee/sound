import struct
import argparse

def read_aydump_file(filename):
    frames = []
    with open(filename, 'r') as file:
        for line in file:
            frame = list(map(int, line.strip().split('\t')))
            frames.append(frame)
    return frames

def write_psg_file(frames, output_filename):
    with open(output_filename, 'wb') as file:
        # Write PSG header
        file.write(b'PSG\x1a')
        file.write(struct.pack('B', 1))  # Version 1
        file.write(b'\x00' * 11)  # Reserved bytes and unknown bytes

        previous_frame = [0] * 14
        for frame in frames:
            for reg, value in enumerate(frame):
                if value != previous_frame[reg]:  # Only write if different from previous frame
                    file.write(struct.pack('B', reg))
                    file.write(struct.pack('B', value))
            file.write(struct.pack('B', 0xFF))  # End of frame marker
            previous_frame = frame.copy()
        
        file.write(struct.pack('B', 0xFD))  # End of PSG data marker

def main(input_filename):
    frames = read_aydump_file(input_filename)
    output_filename = input_filename + '.psg'
    write_psg_file(frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert an AY register dump to a PSG file.')
    parser.add_argument('input_filename', nargs='?', default='sync.psg.aydump', help='The input AY register dump file')
    args = parser.parse_args()
    main(args.input_filename)

    # parser = argparse.ArgumentParser(description='Convert a PSG file to an AY register dump.')
    # parser.add_argument('input_filename', nargs='?', default='sync.psg', help='The input PSG file (default: sync.psg)')
    # args = parser.parse_args()
    # main(args.input_filename)