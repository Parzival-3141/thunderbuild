const std = @import("std");
const eql = std.mem.eql;
const print = std.debug.print;

pub fn parse_args(comptime T: type, allocator: std.mem.Allocator) !ParseResult(T) {
    var args_iter = try std.process.argsWithAllocator(allocator);
    defer args_iter.deinit();

    _ = args_iter.skip(); // Skip executable name

    var result = ParseResult(T){
        .arena = std.heap.ArenaAllocator.init(allocator),
        .arguments = std.mem.zeroInit(T, .{}),
        .success = true,
    };
    errdefer result.deinit();

    while (args_iter.next()) |argh| {
        if (argh[0] != '-') {
            print("Argument '{s}' does not start with '-'.\n", .{argh});
            result.success = false;
            return result;
        }

        const arg = argh[1..];
        print("... Looking for argument named {s}.\n", .{arg});

        var found = false;
        inline for (std.meta.fields(T)) |field| {
            if (std.mem.eql(u8, arg, field.name)) {
                found = true;

                switch (@typeInfo(field.type)) {
                    .Bool => @field(result.arguments, field.name) = true,
                    .Int => {
                        if (get_next_argument(&args_iter, arg, &result.success)) |value| {
                            @field(result.arguments, field.name) = std.fmt.parseInt(field.type, value, 0) catch |err| blk: {
                                print_arg_parse_error(err, arg);
                                result.success = false;
                                break :blk 0;
                            };
                        }
                    },
                    else => {
                        print("Argument '{s}' is of unsupported type '{s}'\n", .{ arg, @typeName(field.type) });
                        result.success = false;
                    },
                }
            }
        }

        if (!found) {
            print("Argument '{s}' is invalid.\n", .{arg});
            result.success = false;
        }
    }

    return result;
}

fn get_next_argument(args_iter: anytype, arg: []const u8, success: *bool) ?[]const u8 {
    if (args_iter.next()) |value| {
        return value;
    } else {
        success.* = false;
        print("Argument '{s}' is missing a value\n", .{arg});
        return null;
    }
}

fn print_arg_parse_error(err: anyerror, arg: []const u8) void {
    print("Error parsing argument '{s}': {s}\n", .{ arg, @errorName(err) });
}

fn ParseResult(comptime T: type) type {
    if (@typeInfo(T) != .Struct) {
        @compileError("Type passed to parse_args is not a Struct!");
    }

    return struct {
        const Self = @This();

        arena: std.heap.ArenaAllocator,

        arguments: T,
        success: bool,

        pub fn deinit(self: Self) void {
            self.arena.deinit();
        }
    };
}
