// Argument parsing inspired by Jon Blow (https://www.youtube.com/watch?v=TwqXTf7VfZk)

const std = @import("std");
const print = @import("main.zig").print;

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
            print("Argument '{s}' does not start with '-'\n", .{argh});
            result.success = false;
            return result;
        }

        const arg = argh[1..];
        //print("... Looking for argument named {s}\n", .{arg});

        var found = false;
        inline for (std.meta.fields(T)) |field| {
            if (std.mem.eql(u8, arg, field.name)) {
                found = true;

                switch (@typeInfo(field.type)) {
                    .Bool => @field(result.arguments, field.name) = true,
                    .Int => {
                        if (get_next_argument(&args_iter, arg, &result.success)) |str| {
                            if (std.fmt.parseInt(field.type, str, 0)) |value| {
                                @field(result.arguments, field.name) = value;
                            } else |err| {
                                print_arg_parse_error(err, arg);
                                result.success = false;
                            }
                        }
                    },
                    .Float => {
                        if (get_next_argument(&args_iter, arg, &result.success)) |str| {
                            if (std.fmt.parseFloat(field.type, str)) |value| {
                                @field(result.arguments, field.name) = value;
                            } else |err| {
                                print_arg_parse_error(err, arg);
                                result.success = false;
                            }
                        }
                    },
                    .Enum => {
                        if (get_next_argument(&args_iter, arg, &result.success)) |str| {
                            if (std.meta.stringToEnum(field.type, str)) |value| {
                                @field(result.arguments, field.name) = value;
                            } else {
                                print("Argument '{s}' has invalid enum value '{s}'\n", .{ arg, str });
                                result.success = false;
                            }
                        }
                    },
                    // Strings
                    .Pointer => |ptr| {
                        if (ptr.size == .Slice and ptr.child == u8) {
                            if (get_next_argument(&args_iter, arg, &result.success)) |str| {

                                // handle sentinel strings
                                if (comptime std.meta.sentinel(field.type)) |sentinel| {
                                    const memory = try result.arena.allocator().alloc(u8, str.len + 1);

                                    std.mem.copy(u8, memory, str);
                                    memory[str.len] = sentinel;

                                    @field(result.arguments, field.name) = memory[0..str.len :sentinel];
                                } else {
                                    @field(result.arguments, field.name) = try result.arena.allocator().dupe(u8, str);
                                }
                            }
                        } else {
                            @compileError("Argument '" ++ field.name ++ "' is of unsupported pointer type '" ++ @typeName(field.type) ++ "', only slices of u8 are supported\n");
                        }
                    },
                    else => {
                        @compileError("Argument '" ++ field.name ++ "' is of unsupported type '" ++ @typeName(field.type) ++ "'\n");
                    },
                }
            }
        }

        if (!found) {
            print("Argument '{s}' is not valid\n", .{arg});
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
