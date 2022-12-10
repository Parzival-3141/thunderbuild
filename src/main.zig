const std = @import("std");
const arguments = @import("arguments.zig");
//const json = std.json;

const MyArguments = struct {
    boolean: bool,
    string: []const u8 = "hello world",
    float: f32,
    int8: i8,
    int16: i16,
};

pub fn main() !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();

    const allocator = arena.allocator();

    const result = try arguments.parse_args(allocator, MyArguments);

    std.debug.print("Success: {any}\n\n", .{result.success});
    // if (!result.success) {
    //     return;
    // }

    print_struct(MyArguments, result.arguments);
}

fn print_struct(comptime T: type, instance: T) void {
    std.debug.print("instance: {s} {{\n", .{@typeName(T)});

    inline for (@typeInfo(T).Struct.fields) |field| {
        const format = if (field.field_type == []const u8) "\"{s}\"" else "{any}";
        std.debug.print("    {s}: {s} = " ++ format ++ "\n", .{ field.name, @typeName(field.field_type), @field(instance, field.name) });
    }

    std.debug.print("}}\n", .{});
}

pub fn print(comptime text: []const u8, args: anytype) !void {
    var bw = std.io.bufferedWriter(std.io.getStdOut().writer());
    const stdout = bw.writer();

    try stdout.print(text, args);

    try bw.flush(); // don't forget to flush!
}

test "string interpolation" {
    const format = "s";
    std.debug.print("\n{s}: {" ++ format ++ "}\n", .{ "test", "hello world" });
}
