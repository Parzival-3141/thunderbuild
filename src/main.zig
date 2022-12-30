const std = @import("std");
const arguments = @import("arguments.zig");
const json = std.json;

const ThunderBuildArgs = struct {
    version: []const u8,
    overwrite: bool = false,
    output_dir: []const u8 = "./thunder_builds/",
    info_file: []const u8 = "./thunder_info.json",
    help: bool,

    const help_txt =
        \\Usage: thunderbuild [OPTIONS]
        \\
        \\OPTIONS:
        \\    -version    <string>   Version to mark the build as. Overrides versioning in the Thunder Info file.
        \\                           Follows Semantic Versioning (major.minor.patch).
        \\    -overwrite             Overwrite a build if one with the same version already exists in output_dir.
        \\    -output_dir <path>     Directory to output the build. Defaults to "./thunder_builds/".
        \\    -info_file  <path>     Path to a Thunder Info file. Defaults to "./thunder_info.json".
        \\    -help                  Display this help text.
        \\    
        \\Relative paths are treated as relative to the current working directory.
        \\In Thunder Info files, paths are relative to the file location.
    ;
};

const ThunderBuildInfo = struct {
    version_file: ?[]const u8 = null,
    version_regex: ?[]const u8 = null,
    output_dir: ?[]const u8 = null,

    icon: []const u8,
    readme: []const u8,
    mod_files: [][2][]const u8, // array of arrays of two strings

    manifest: struct {
        name: []const u8,
        version_number: []const u8,
        website_url: []const u8,
        description: []const u8,
        dependencies: [][]const u8,
    },
};

pub fn main() !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();

    const allocator = arena.allocator();

    const result = try arguments.parse_args(ThunderBuildArgs, allocator);
    defer result.deinit();

    std.debug.print("Arg Parsing Success: {any}\n\n", .{result.success});
    // if (!result.success or result.arguments.help) {
    //     print("{s}\n\n", .{ThunderBuildArgs.help_txt});
    //     return;
    // }

    //print_struct(ThunderBuildArgs, result.arguments);
    const args = result.arguments;

    const realpath = std.fs.realpathAlloc(allocator, args.info_file) catch args.info_file;

    const json_file = std.fs.cwd().readFileAlloc(allocator, args.info_file, 1024) catch |err| {
        print("Error opening Thunder Info file: {s} at '{s}'\n", .{ @errorName(err), realpath });
        return;
    };

    const json_parse_options = json.ParseOptions{ .allocator = allocator, .ignore_unknown_fields = false };
    var token_stream = json.TokenStream.init(json_file);

    const build_info = json.parse(ThunderBuildInfo, &token_stream, json_parse_options) catch |err| {
        // @Todo: print where parsing failed in the file
        print("Error parsing Thunder Info file: {s} in '{s}'\n", .{ @errorName(err), realpath });
        return;
    };
    defer json.parseFree(ThunderBuildInfo, build_info, json_parse_options);

    print("{s}", .{try json.stringifyAlloc(allocator, build_info, .{ .whitespace = .{ .indent = .Tab } })});
}

fn print_struct(comptime T: type, instance: T) void {
    std.debug.print("instance: {s} {{\n", .{@typeName(T)});

    inline for (@typeInfo(T).Struct.fields) |field| {
        const format = switch (field.type) {
            []const u8 => "\"{s}\"",
            ?[]const u8 => "{?s}",
            else => "{any}",
        };

        std.debug.print("    {s}: {s} = " ++ format ++ "\n", .{ field.name, @typeName(field.type), @field(instance, field.name) });
    }

    std.debug.print("}}\n", .{});
}

pub fn print(comptime text: []const u8, args: anytype) void {
    var bw = std.io.bufferedWriter(std.io.getStdOut().writer());
    const stdout = bw.writer();

    stdout.print(text, args) catch unreachable;
    bw.flush() catch unreachable; // don't forget to flush!
}
