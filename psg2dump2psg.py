import struct
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

def write_psg_file(frames, output_filename):
    with open(output_filename, 'wb') as file:
        # Write PSG header
        file.write(b'PSG\x1a')
        file.write(struct.pack('B', 0))  # Version from original file
        file.write(b'\x00' * 11)  # Reserved bytes and unknown bytes

        for frame in frames:
            file.write(struct.pack('B', 0xFF))  # start of frame marker
            for reg, value in enumerate(frame):
                print(reg, value)
                if value is not None:  # Only write if the value is provided
                    file.write(struct.pack('B', reg))
                    file.write(struct.pack('B', value))
                    frame_updated = True

        file.write(struct.pack('B', 0xFF))  # End of PSG data marker

def main(input_filename):
    frames = read_aydump_file(input_filename)
    output_filename = input_filename + '.psg'
    write_psg_file(frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert an AY register dump to a PSG file.')
    parser.add_argument('input_filename', nargs='?', default='sync.psg.aydump', help='The input AY register dump file')
    args = parser.parse_args()
    main(args.input_filename)
