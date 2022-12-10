const std = @import("std");
const eql = std.mem.eql;
const print = std.debug.print;

pub fn parse_args(allocator: std.mem.Allocator, comptime T: type) !struct { success: bool, arguments: T } {
    var success = true;
    var result = std.mem.zeroInit(T, .{});

    const fields = comptime switch (@typeInfo(T)) {
        .Struct => |info| info.fields,
        else => {
            print("Type passed to parse_args is not a struct!", .{});
            return .{ .success = false, .arguments = result };
        },
    };

    var args = try std.process.argsWithAllocator(allocator);
    defer args.deinit();

    _ = args.skip(); // Skip call to executable

    while (args.next()) |argh| {
        if (argh[0] != '-') {
            std.debug.print("Argument '{s}' does not start with '-'.\n", .{argh});
            return .{ .success = false, .arguments = result };
        }

        const arg = argh[1..];
        print("... Looking for argument named {s}.\n", .{arg});

        for (fields) |field| {
            if (!eql(u8, field.name, arg)) continue;
        }
    }

    return .{ .success = success, .arguments = result };
}

// @Todo: store StructField name and type comptime info for use at runtime
const Type = enum { BOOL, INTEGER, FLOAT, STRING };
